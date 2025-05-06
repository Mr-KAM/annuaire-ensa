import os
from flask import Flask                                 # pip install flask
from flask_sqlalchemy import SQLAlchemy                 # pip install flask-sqlalchemy
from flask_migrate import Migrate                       # pip install flask-migrate
from flask_login import LoginManager                    # pip install flask-login
from mailer import Mailer                               # pip install quick-mailer
from pushbullet import Pushbullet                       # pip install pushbullet.py
from datetime import datetime
import requests
import json
import secrets                                          # pip install secrets
from dotenv import load_dotenv                          # pip install python-dotenv


# Chargement des variables d'environnement depuis .env
load_dotenv()
# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Initialiser Mailer pour l'envoi d'emails
mail = Mailer(
        email=os.environ["EMAIL_MESSAGERIE"],
        password=os.environ["EMAIL_MESSAGERIE_PASSWORD"]
)

# Initialiser Pushbullet pour les notifications SMS
pb = Pushbullet(os.environ["PUSHBULLET_KEY"])


# Fonctions utilitaires
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_mail(mail, objet, message, destination):
    mail.send(receiver=destination, subject=objet, message=message)
    print("====STATUS MESSAGE:", mail.status)
    print(f"+++ Email envoyé à {destination} avec succès:  +++++++++")
    return mail.status

# def sendSmsOld(pb,message, contact_number):
#     # Numéro de téléphone est au format international (ex. +1234567890) avec l'indicatif du pays
#     print(f"Message SMS envoyé avec succès au {contact_number} à {datetime.now()}")
#     phone = pb.devices[0]
#     print(phone)
#     pb.push_sms(phone, contact_number, message)

def sendSms(pb, message, contact_number):
    """
    Envoie un SMS via Pushbullet (nouvelle méthode /v2/texts)

    Paramètres:
    - pb : objet Pushbullet déjà initialisé
    - message : texte à envoyer
    - contact_number : numéro du destinataire en format international (+225...)
    """

    # Récupérer la clé API Pushbullet depuis l'objet pb
    api_key = pb.api_key

    # Récupérer le téléphone qui peut envoyer les SMS
    phone = next((device for device in pb.devices if device.has_sms), None)

    if not phone:
        raise Exception("Aucun appareil compatible SMS trouvé sur votre compte Pushbullet.")

    phone_iden = phone.device_iden

    url = "https://api.pushbullet.com/v2/texts"
    headers = {
        "Access-Token": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "addresses": [contact_number],
            "message": message,
            "target_device_iden": phone_iden
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(f"✅ Message SMS envoyé avec succès au {contact_number} à {datetime.now()}")
    else:
        print(f"❌ Échec de l'envoi du SMS au {contact_number} à {datetime.now()}")
        print(f"Erreur Pushbullet : {response.text}")
        raise Exception(f"Erreur Pushbullet : {response.text}")


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///annuaire.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['UPLOAD_FOLDER_PHOTOS'] = os.path.join('static', 'uploads', 'photos')
    app.config['UPLOAD_FOLDER_CV'] = os.path.join('static', 'uploads', 'cv')
    app.config['ALLOWED_EXTENSIONS_PHOTO'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['ALLOWED_EXTENSIONS_CV'] = {'pdf'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload



    # Création des dossiers d'upload s'ils n'existent pas
    os.makedirs(app.config['UPLOAD_FOLDER_PHOTOS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_CV'], exist_ok=True)

    # Initialiser les extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    # Importation et ajout à app des blueprints des differents 'route' de l'application
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.annuaire import annuaire_bp
    from routes.index import index_bp
    from routes.info import info_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(annuaire_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(chat_bp)

    # Fonctions utilitaires et processeurs de contexte
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        if value:
            return value.strftime(format)
        return ''

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
