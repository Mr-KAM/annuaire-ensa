import os
import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from __init__ import db, allowed_file
from models import User, UserProfile, RoleEnum, PromotionEnum, SpecialiteEnum, StatutProfessionnelEnum
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Fonction utilitaire pour générer un mot de passe aléatoire
def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Fonction utilitaire pour simuler l'envoi d'un SMS
def send_sms(phone_number, message):
    # Dans une application réelle, cette fonction utiliserait une API comme Twilio
    # Pour cette démo, on simule juste l'envoi
    print(f"SMS envoyé à {phone_number}: {message}")
    return True

# Fonction utilitaire pour simuler l'envoi d'un email
def send_email(email, subject, message):
    # Dans une application réelle, cette fonction utiliserait une API comme SendGrid
    # Pour cette démo, on simule juste l'envoi
    print(f"Email envoyé à {email} avec le sujet '{subject}': {message}")
    return True

@admin_bp.route('/')
@login_required
def dashboard():
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'accès à cette page.", 'danger')
        return redirect(url_for('index.index'))

    # Récupérer tous les profils
    profiles = UserProfile.query.all()

    return render_template('admin/dashboard.html', profiles=profiles)

@admin_bp.route('/add-member', methods=['GET', 'POST'])
@login_required
def add_member():
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'accès à cette page.", 'danger')
        return redirect(url_for('index.index'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        email = request.form.get('email')
        nom_prenoms = request.form.get('nom_prenoms')

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(f"Un utilisateur avec l'email {email} existe déjà.", 'danger')
            return redirect(url_for('admin.add_member'))

        # Créer un nouvel utilisateur
        password = generate_password()
        new_user = User(email=email, role=RoleEnum.USER)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Pour obtenir l'ID de l'utilisateur

        # Créer un profil pour l'utilisateur
        new_profile = UserProfile(
            user_id=new_user.id,
            nom_prenoms=nom_prenoms,
            email=email,
            promotion=request.form.get('promotion'),
            specialite=request.form.get('specialite'),
            structure=request.form.get('structure'),
            fonction=request.form.get('fonction'),
            localite_residence=request.form.get('localite_residence'),
            numero_whatsapp=request.form.get('numero_whatsapp'),
            autres_numeros=request.form.get('autres_numeros'),
            compte_linkedin=request.form.get('compte_linkedin'),
            biographie=request.form.get('biographie'),
            statut_professionnel=request.form.get('statut_professionnel'),
            is_mentor_available='is_mentor_available' in request.form
        )

        # Gestion de l'upload de la photo de profil
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename != '' and allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS_PHOTO']):
                filename = secure_filename(photo_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER_PHOTOS'], unique_filename)
                photo_file.save(photo_path)
                new_profile.photo_filename = unique_filename

        # Gestion de l'upload du CV
        if 'cv' in request.files:
            cv_file = request.files['cv']
            if cv_file and cv_file.filename != '' and allowed_file(cv_file.filename, current_app.config['ALLOWED_EXTENSIONS_CV']):
                filename = secure_filename(cv_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                cv_path = os.path.join(current_app.config['UPLOAD_FOLDER_CV'], unique_filename)
                cv_file.save(cv_path)
                new_profile.cv_filename = unique_filename

        db.session.add(new_profile)
        db.session.commit()

        # Envoyer un email avec les identifiants
        email_subject = "Bienvenue dans l'annuaire des alumni"
        email_message = f"""
        Bonjour {nom_prenoms},

        Votre compte a été créé dans l'annuaire des alumni.

        Voici vos identifiants de connexion:
        Email: {email}
        Mot de passe: {password}

        Nous vous invitons à vous connecter et à compléter votre profil.

        Cordialement,
        L'équipe de l'annuaire
        """
        send_email(email, email_subject, email_message)

        # Envoyer un SMS si un numéro WhatsApp est fourni
        if new_profile.numero_whatsapp:
            sms_message = f"Bienvenue dans l'annuaire des alumni! Vos identifiants: Email: {email}, Mot de passe: {password}"
            send_sms(new_profile.numero_whatsapp, sms_message)

        flash(f"Le membre {nom_prenoms} a été ajouté avec succès. Un email et un SMS ont été envoyés avec les identifiants.", 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_member.html',
                          promotions=PromotionEnum,
                          specialites=SpecialiteEnum,
                          statuts=StatutProfessionnelEnum)

@admin_bp.route('/edit-member/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_member(user_id):
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'accès à cette page.", 'danger')
        return redirect(url_for('index.index'))

    # Récupérer le profil de l'utilisateur
    user_profile = UserProfile.query.filter_by(user_id=user_id).first_or_404()

    if request.method == 'POST':
        # Mettre à jour les informations du profil
        user_profile.nom_prenoms = request.form.get('nom_prenoms')
        user_profile.email = request.form.get('email')
        user_profile.promotion = request.form.get('promotion')
        user_profile.specialite = request.form.get('specialite')
        user_profile.structure = request.form.get('structure')
        user_profile.fonction = request.form.get('fonction')
        user_profile.localite_residence = request.form.get('localite_residence')
        user_profile.numero_whatsapp = request.form.get('numero_whatsapp')
        user_profile.autres_numeros = request.form.get('autres_numeros')
        user_profile.compte_linkedin = request.form.get('compte_linkedin')
        user_profile.biographie = request.form.get('biographie')
        user_profile.statut_professionnel = request.form.get('statut_professionnel')
        user_profile.is_mentor_available = 'is_mentor_available' in request.form

        # Gestion de l'upload de la photo de profil
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename != '' and allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS_PHOTO']):
                filename = secure_filename(photo_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER_PHOTOS'], unique_filename)
                photo_file.save(photo_path)
                user_profile.photo_filename = unique_filename

        # Gestion de l'upload du CV
        if 'cv' in request.files:
            cv_file = request.files['cv']
            if cv_file and cv_file.filename != '' and allowed_file(cv_file.filename, current_app.config['ALLOWED_EXTENSIONS_CV']):
                filename = secure_filename(cv_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                cv_path = os.path.join(current_app.config['UPLOAD_FOLDER_CV'], unique_filename)
                cv_file.save(cv_path)
                user_profile.cv_filename = unique_filename

        db.session.commit()

        flash(f"Le profil de {user_profile.nom_prenoms} a été mis à jour avec succès.", 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_member.html',
                          profile=user_profile,
                          promotions=PromotionEnum,
                          specialites=SpecialiteEnum,
                          statuts=StatutProfessionnelEnum)

@admin_bp.route('/delete-member/<int:user_id>', methods=['POST'])
@login_required
def delete_member(user_id):
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': "Vous n'avez pas les droits d'accès à cette action."}), 403

    # Récupérer l'utilisateur et son profil
    user = User.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if profile:
        # Supprimer les fichiers associés
        if profile.photo_filename:
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER_PHOTOS'], profile.photo_filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        if profile.cv_filename:
            cv_path = os.path.join(current_app.config['UPLOAD_FOLDER_CV'], profile.cv_filename)
            if os.path.exists(cv_path):
                os.remove(cv_path)

        db.session.delete(profile)

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': "Le membre a été supprimé avec succès."})

@admin_bp.route('/reset-password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': "Vous n'avez pas les droits d'accès à cette action."}), 403

    # Récupérer l'utilisateur
    user = User.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    # Générer un nouveau mot de passe
    new_password = generate_password()
    user.set_password(new_password)
    db.session.commit()

    # Envoyer un email avec le nouveau mot de passe
    if profile:
        email_subject = "Réinitialisation de votre mot de passe"
        email_message = f"""
        Bonjour {profile.nom_prenoms},

        Votre mot de passe a été réinitialisé.

        Voici vos nouveaux identifiants de connexion:
        Email: {user.email}
        Mot de passe: {new_password}

        Nous vous invitons à vous connecter et à changer votre mot de passe.

        Cordialement,
        L'équipe de l'annuaire
        """
        send_email(user.email, email_subject, email_message)

        # Envoyer un SMS si un numéro WhatsApp est fourni
        if profile.numero_whatsapp:
            sms_message = f"Votre mot de passe a été réinitialisé. Nouveau mot de passe: {new_password}"
            send_sms(profile.numero_whatsapp, sms_message)

    return jsonify({'success': True, 'message': "Le mot de passe a été réinitialisé et envoyé à l'utilisateur."})
