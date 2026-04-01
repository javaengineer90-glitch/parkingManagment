from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from models.booking import (
    create_booking, get_booking_by_id, get_bookings_by_user,
    get_active_bookings_by_user, end_booking, cancel_booking,
    check_spot_conflict, get_bookings_for_spot_owner
)
from models.parking_spot import get_spot_by_id
from models.payment import create_payment, update_payment_status, get_payment_by_booking
from services.billing import calculate_billing, calculate_prorated
from services.notification import (
    notify_booking_confirmed, notify_spot_booked,
    notify_booking_ended, notify_booking_cancelled, notify_payment_received
)
from services.payment import create_razorpay_order

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/book/<int:spot_id>', methods=['GET', 'POST'])
@login_required
def book_spot(spot_id):
    spot = get_spot_by_id(spot_id)
    if not spot or not spot['is_available']:
        flash('Spot not available.', 'danger')
        return redirect(url_for('spots.list_spots'))

    if spot['owner_id'] == current_user.id:
        flash('You cannot book your own spot.', 'warning')
        return redirect(url_for('spots.list_spots'))

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type = request.form.get('vehicle_type', 'car')
        start_time = request.form.get('start_time', '')
        end_time = request.form.get('end_time', '')

        if not all([vehicle_number, start_time, end_time]):
            flash('All fields are required.', 'danger')
            return render_template('bookings/book.html', spot=spot)

        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except ValueError:
            flash('Invalid date/time format.', 'danger')
            return render_template('bookings/book.html', spot=spot)

        if end_dt <= start_dt:
            flash('End time must be after start time.', 'danger')
            return render_template('bookings/book.html', spot=spot)

        if check_spot_conflict(spot_id, start_time, end_time):
            flash('This spot is already booked for the selected time slot.', 'danger')
            return render_template('bookings/book.html', spot=spot)

        total_hours, total_amount = calculate_billing(spot['hourly_rate'], start_dt, end_dt)

        booking_id = create_booking(
            spot_id, current_user.id, vehicle_number, vehicle_type,
            start_time, end_time, total_hours, total_amount
        )

        # Create payment
        order = create_razorpay_order(total_amount)
        payment_id = create_payment(
            booking_id, current_user.id, total_amount,
            'demo' if order.get('demo') else 'razorpay',
            order['id']
        )

        if order.get('demo'):
            update_payment_status(payment_id, 'completed', order['id'])
            notify_booking_confirmed(current_user.id, spot['spot_number'], start_time, end_time)
            notify_spot_booked(spot['owner_id'], spot['spot_number'], current_user.name, start_time, end_time)
            notify_payment_received(spot['owner_id'], total_amount, spot['spot_number'], current_user.name)
            flash(f'Booking confirmed! Total: Rs. {total_amount} for {total_hours} hour(s). (Demo payment)', 'success')
            return redirect(url_for('bookings.my_bookings'))

        # For real Razorpay, redirect to payment page
        from flask import current_app
        return render_template('payments/checkout.html',
                               order=order,
                               payment_id=payment_id,
                               booking_id=booking_id,
                               key_id=current_app.config['RAZORPAY_KEY_ID'],
                               amount=total_amount,
                               spot=spot)

    return render_template('bookings/book.html', spot=spot)


@bookings_bp.route('/bookings')
@login_required
def my_bookings():
    bookings = get_bookings_by_user(current_user.id)
    return render_template('bookings/my_bookings.html', bookings=bookings)


@bookings_bp.route('/bookings/active')
@login_required
def active_bookings():
    bookings = get_active_bookings_by_user(current_user.id)
    return render_template('bookings/active.html', bookings=bookings)


@bookings_bp.route('/bookings/received')
@login_required
def received_bookings():
    bookings = get_bookings_for_spot_owner(current_user.id)
    return render_template('bookings/received.html', bookings=bookings)


@bookings_bp.route('/bookings/end/<int:booking_id>')
@login_required
def end_booking_early(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking or booking['booked_by'] != current_user.id or booking['status'] != 'active':
        flash('Invalid booking.', 'danger')
        return redirect(url_for('bookings.my_bookings'))

    actual_end = datetime.now().isoformat()
    total_hours, total_amount = calculate_prorated(booking['hourly_rate'], booking['start_time'], actual_end)
    end_booking(booking_id, actual_end, total_hours, total_amount)

    # Update payment amount if prorated is less
    payment = get_payment_by_booking(booking_id)
    if payment and total_amount != payment['amount']:
        from db import get_db
        db = get_db()
        db.execute("UPDATE payments SET amount = ? WHERE id = ?", (total_amount, payment['id']))
        db.commit()

    notify_booking_ended(current_user.id, booking['spot_number'], total_amount)
    flash(f'Booking ended. Pro-rated charge: Rs. {total_amount} for {total_hours} hour(s).', 'success')
    return redirect(url_for('bookings.my_bookings'))


@bookings_bp.route('/bookings/cancel/<int:booking_id>')
@login_required
def cancel_booking_route(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking or booking['booked_by'] != current_user.id or booking['status'] != 'active':
        flash('Invalid booking.', 'danger')
        return redirect(url_for('bookings.my_bookings'))

    cancel_booking(booking_id)

    payment = get_payment_by_booking(booking_id)
    if payment:
        update_payment_status(payment['id'], 'refunded')

    notify_booking_cancelled(booking['owner_id'], booking['spot_number'], current_user.name)
    flash('Booking cancelled.', 'info')
    return redirect(url_for('bookings.my_bookings'))
