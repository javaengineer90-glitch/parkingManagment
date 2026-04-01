from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
import db

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from models.user import get_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    from routes.auth import auth_bp
    from routes.spots import spots_bp
    from routes.bookings import bookings_bp
    from routes.payments import payments_bp
    from routes.admin import admin_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(spots_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)

    @app.route('/')
    def index():
        return redirect(url_for('spots.list_spots'))

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        if current_user.is_authenticated:
            from models.notification import get_unread_count
            return {'unread_notification_count': get_unread_count(current_user.id)}
        return {'unread_notification_count': 0}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
