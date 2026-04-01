from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models.user import get_all_users, toggle_user_active
from models.parking_spot import get_all_spots
from models.booking import get_all_bookings, get_active_bookings_count
from models.payment import (
    get_all_payments, get_total_revenue, get_revenue_today,
    get_revenue_this_month, get_daily_revenue
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('spots.list_spots'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'total_users': len(get_all_users()),
        'total_spots': len(get_all_spots()),
        'active_bookings': get_active_bookings_count(),
        'total_revenue': get_total_revenue(),
        'revenue_today': get_revenue_today(),
        'revenue_month': get_revenue_this_month(),
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@admin_required
def users():
    all_users = get_all_users()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/toggle/<int:user_id>')
@admin_required
def toggle_user(user_id):
    if user_id == current_user.id:
        flash('Cannot deactivate yourself.', 'warning')
        return redirect(url_for('admin.users'))
    toggle_user_active(user_id)
    flash('User status updated.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/bookings')
@admin_required
def bookings():
    all_bookings = get_all_bookings()
    return render_template('admin/bookings.html', bookings=all_bookings)


@admin_bp.route('/payments')
@admin_required
def payments():
    all_payments = get_all_payments()
    return render_template('admin/payments.html', payments=all_payments)


@admin_bp.route('/reports')
@admin_required
def reports():
    daily = get_daily_revenue(30)
    stats = {
        'total_revenue': get_total_revenue(),
        'revenue_today': get_revenue_today(),
        'revenue_month': get_revenue_this_month(),
        'total_bookings': len(get_all_bookings()),
        'active_bookings': get_active_bookings_count(),
    }
    return render_template('admin/reports.html', daily_revenue=daily, stats=stats)
