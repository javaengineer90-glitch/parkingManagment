from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.parking_spot import (
    create_spot, get_available_spots, get_spots_by_owner,
    get_spot_by_id, update_spot, toggle_spot_availability, delete_spot
)
from models.booking import get_active_bookings_for_spots

spots_bp = Blueprint('spots', __name__)


@spots_bp.route('/spots')
def list_spots():
    spots = get_available_spots()
    spot_ids = [s['id'] for s in spots]
    active_bookings = get_active_bookings_for_spots(spot_ids)
    bookings_by_spot = {}
    for b in active_bookings:
        bookings_by_spot.setdefault(b['spot_id'], []).append(b)
    return render_template('spots/list.html', spots=spots, bookings_by_spot=bookings_by_spot)


@spots_bp.route('/my-spots')
@login_required
def my_spots():
    spots = get_spots_by_owner(current_user.id)
    spot_ids = [s['id'] for s in spots]
    active_bookings = get_active_bookings_for_spots(spot_ids)
    bookings_by_spot = {}
    for b in active_bookings:
        bookings_by_spot.setdefault(b['spot_id'], []).append(b)
    return render_template('spots/my_spots.html', spots=spots, bookings_by_spot=bookings_by_spot)


@spots_bp.route('/spots/add', methods=['GET', 'POST'])
@login_required
def add_spot():
    if request.method == 'POST':
        spot_number = request.form.get('spot_number', '').strip()
        location_description = request.form.get('location_description', '').strip()
        hourly_rate = request.form.get('hourly_rate', '0')
        available_from = request.form.get('available_from', '')
        available_until = request.form.get('available_until', '')

        if not spot_number or not hourly_rate:
            flash('Spot number and hourly rate are required.', 'danger')
            return render_template('spots/add_edit.html', spot=None)

        try:
            hourly_rate = float(hourly_rate)
            if hourly_rate <= 0:
                raise ValueError
        except ValueError:
            flash('Hourly rate must be a positive number.', 'danger')
            return render_template('spots/add_edit.html', spot=None)

        create_spot(current_user.id, spot_number, location_description, hourly_rate, available_from, available_until)
        flash('Parking spot added successfully!', 'success')
        return redirect(url_for('spots.my_spots'))

    return render_template('spots/add_edit.html', spot=None)


@spots_bp.route('/spots/edit/<int:spot_id>', methods=['GET', 'POST'])
@login_required
def edit_spot(spot_id):
    spot = get_spot_by_id(spot_id)
    if not spot or spot['owner_id'] != current_user.id:
        flash('Spot not found or unauthorized.', 'danger')
        return redirect(url_for('spots.my_spots'))

    if request.method == 'POST':
        spot_number = request.form.get('spot_number', '').strip()
        location_description = request.form.get('location_description', '').strip()
        hourly_rate = request.form.get('hourly_rate', '0')
        available_from = request.form.get('available_from', '')
        available_until = request.form.get('available_until', '')

        try:
            hourly_rate = float(hourly_rate)
            if hourly_rate <= 0:
                raise ValueError
        except ValueError:
            flash('Hourly rate must be a positive number.', 'danger')
            return render_template('spots/add_edit.html', spot=spot)

        update_spot(spot_id, spot_number, location_description, hourly_rate, available_from, available_until)
        flash('Spot updated successfully!', 'success')
        return redirect(url_for('spots.my_spots'))

    return render_template('spots/add_edit.html', spot=spot)


@spots_bp.route('/spots/toggle/<int:spot_id>')
@login_required
def toggle_spot(spot_id):
    spot = get_spot_by_id(spot_id)
    if not spot or spot['owner_id'] != current_user.id:
        flash('Spot not found or unauthorized.', 'danger')
        return redirect(url_for('spots.my_spots'))

    toggle_spot_availability(spot_id)
    flash('Spot availability toggled.', 'success')
    return redirect(url_for('spots.my_spots'))


@spots_bp.route('/spots/delete/<int:spot_id>')
@login_required
def remove_spot(spot_id):
    spot = get_spot_by_id(spot_id)
    if not spot or spot['owner_id'] != current_user.id:
        flash('Spot not found or unauthorized.', 'danger')
        return redirect(url_for('spots.my_spots'))

    delete_spot(spot_id)
    flash('Spot deleted.', 'success')
    return redirect(url_for('spots.my_spots'))
