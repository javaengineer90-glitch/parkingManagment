from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.payment import get_payments_by_user, get_earnings_by_owner, update_payment_status, get_payment_by_id
from models.booking import get_booking_by_id
from services.payment import verify_razorpay_payment
from services.notification import notify_booking_confirmed, notify_spot_booked, notify_payment_received

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/payments')
@login_required
def payment_history():
    payments = get_payments_by_user(current_user.id)
    return render_template('payments/history.html', payments=payments)


@payments_bp.route('/earnings')
@login_required
def earnings():
    earnings_list = get_earnings_by_owner(current_user.id)
    total = sum(e['amount'] for e in earnings_list)
    return render_template('payments/earnings.html', earnings=earnings_list, total=total)


@payments_bp.route('/payments/verify', methods=['POST'])
@login_required
def verify_payment():
    payment_id = request.form.get('payment_id')
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')
    booking_id = request.form.get('booking_id')

    if verify_razorpay_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature):
        update_payment_status(int(payment_id), 'completed', razorpay_payment_id)

        booking = get_booking_by_id(int(booking_id))
        if booking:
            notify_booking_confirmed(current_user.id, booking['spot_number'], booking['start_time'], booking['end_time'])
            notify_spot_booked(booking['owner_id'], booking['spot_number'], current_user.name, booking['start_time'], booking['end_time'])
            notify_payment_received(booking['owner_id'], booking['total_amount'], booking['spot_number'], current_user.name)

        flash('Payment successful! Booking confirmed.', 'success')
    else:
        update_payment_status(int(payment_id), 'failed')
        flash('Payment verification failed.', 'danger')

    return redirect(url_for('bookings.my_bookings'))
