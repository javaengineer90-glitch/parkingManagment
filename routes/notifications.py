from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.notification import get_notifications, mark_as_read, mark_all_read

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def list_notifications():
    notifs = get_notifications(current_user.id)
    return render_template('notifications/list.html', notifications=notifs)


@notifications_bp.route('/notifications/read/<int:notif_id>')
@login_required
def read_notification(notif_id):
    mark_as_read(notif_id)
    return redirect(url_for('notifications.list_notifications'))


@notifications_bp.route('/notifications/read-all')
@login_required
def read_all():
    mark_all_read(current_user.id)
    return redirect(url_for('notifications.list_notifications'))
