from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from __init__ import db
from models import User, UserProfile, RoleEnum
import random
import string

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            user.last_login = db.func.now()
            db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('profile.view_profile'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Génération d'un mot de passe temporaire
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.set_password(temp_password)
            db.session.commit()

            # Ici, on simulerait l'envoi d'un email avec le mot de passe temporaire
            flash(f'Un nouveau mot de passe a été envoyé à {email}. (Pour les besoins de la démo: {temp_password})', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Aucun compte associé à cet email.', 'danger')

    return render_template('auth/reset_password.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Mot de passe actuel incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Votre mot de passe a été mis à jour avec succès.', 'success')
            return redirect(url_for('profile.view_profile'))

    return render_template('auth/change_password.html')
