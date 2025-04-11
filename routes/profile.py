import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from __init__ import db, allowed_file
from models import User, UserProfile, PromotionEnum, SpecialiteEnum, StatutProfessionnelEnum
import uuid

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view_profile():
    # Récupérer le profil de l'utilisateur connecté
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    # Si l'utilisateur n'a pas encore de profil, le rediriger vers la page de création
    if not user_profile:
        return redirect(url_for('profile.edit_profile'))

    return render_template('profile/view.html', profile=user_profile)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Récupérer le profil existant ou en créer un nouveau
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    if not user_profile:
        user_profile = UserProfile(
            user_id=current_user.id,
            email=current_user.email,
            nom_prenoms=""
        )

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
                # Générer un nom de fichier unique
                filename = secure_filename(photo_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"

                # Sauvegarder le fichier
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER_PHOTOS'], unique_filename)
                photo_file.save(photo_path)

                # Mettre à jour le nom du fichier dans la base de données
                user_profile.photo_filename = unique_filename

        # Gestion de l'upload du CV
        if 'cv' in request.files:
            cv_file = request.files['cv']
            if cv_file and cv_file.filename != '' and allowed_file(cv_file.filename, current_app.config['ALLOWED_EXTENSIONS_CV']):
                # Générer un nom de fichier unique
                filename = secure_filename(cv_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"

                # Sauvegarder le fichier
                cv_path = os.path.join(current_app.config['UPLOAD_FOLDER_CV'], unique_filename)
                cv_file.save(cv_path)

                # Mettre à jour le nom du fichier dans la base de données
                user_profile.cv_filename = unique_filename

        # Sauvegarder les modifications
        if not user_profile.id:
            db.session.add(user_profile)
        db.session.commit()

        flash('Votre profil a été mis à jour avec succès.', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile/edit.html',
                          profile=user_profile,
                          promotions=PromotionEnum,
                          specialites=SpecialiteEnum,
                          statuts=StatutProfessionnelEnum)

@profile_bp.route('/user/<int:user_id>')
@login_required
def view_user_profile(user_id):
    # Vérifier si l'utilisateur existe
    user_profile = UserProfile.query.filter_by(user_id=user_id).first_or_404()

    return render_template('profile/view.html', profile=user_profile)

@profile_bp.route('/cv/<filename>')
@login_required
def download_cv(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_CV'], filename)
