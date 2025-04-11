from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from __init__ import db
from models import UserProfile

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    # Si l'utilisateur est connecté, récupérer quelques statistiques
    stats = {}
    if current_user.is_authenticated:
        stats['total_members'] = UserProfile.query.count()
        stats['mentors_available'] = UserProfile.query.filter_by(is_mentor_available=True).count()

    return render_template('landing/index.html', stats=stats)

@index_bp.route('/home')
def home():
    # Redirection vers la page appropriée en fonction de l'authentification
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('annuaire.index'))
    else:
        return redirect(url_for('auth.login'))
