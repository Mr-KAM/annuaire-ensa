import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message
from datetime import datetime
import secrets

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Utility functions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///annuaire.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER_PHOTOS'] = os.path.join('static', 'uploads', 'photos')
    app.config['UPLOAD_FOLDER_CV'] = os.path.join('static', 'uploads', 'cv')
    app.config['ALLOWED_EXTENSIONS_PHOTO'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['ALLOWED_EXTENSIONS_CV'] = {'pdf'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['MAIL_SERVER'] = 'your_mail_server'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'your_username'
    app.config['MAIL_PASSWORD'] = 'your_password'
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

    mail = Mail(app)

    # Création des dossiers d'upload s'ils n'existent pas
    os.makedirs(app.config['UPLOAD_FOLDER_PHOTOS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_CV'], exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.annuaire import annuaire_bp
    from routes.index import index_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(annuaire_bp)
    app.register_blueprint(index_bp)

    # Utility functions and context processors
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        if value:
            return value.strftime(format)
        return ''

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
