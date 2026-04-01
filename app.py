import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from config import get_config
import db

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        log_dir = os.path.join(app.root_path, 'logs')
        try:
            os.makedirs(log_dir, exist_ok=True)
        except PermissionError:
            # Fallback to stdout logging when filesystem is not writable
            fallback_handler = logging.StreamHandler()
            fallback_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            fallback_handler.setLevel(logging.INFO)
            app.logger.addHandler(fallback_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Parking Management App startup (stdout fallback, log dir unavailable)')
            return

        log_file = os.path.join(log_dir, 'parking_app.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Parking Management App startup')


def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # Setup logging
    setup_logging(app)
    
    # User loader
    from models.user import get_user_by_id
    
    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))
    
    # Register blueprints
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
    
    # Routes
    @app.route('/')
    def index():
        return redirect(url_for('spots.list_spots'))
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {'status': 'healthy'}, 200
    
    # Context processors
    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        if current_user.is_authenticated:
            from models.notification import get_unread_count
            return {'unread_notification_count': get_unread_count(current_user.id)}
        return {'unread_notification_count': 0}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return {'error': 'Internal server error'}, 500
    
    return app


if __name__ == '__main__':
    # Development only
    app = create_app()
    app.run(debug=True, host='127.0.0.1')
