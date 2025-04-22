import os
import random
import string
import csv
import pandas as pd
import io
from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from __init__ import db, allowed_file, mail, send_mail, pb, sendSms
from models import User, UserProfile, RoleEnum, PromotionEnum, SpecialiteEnum, StatutProfessionnelEnum
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Fonction utilitaire pour générer un mot de passe aléatoire
def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Fonction pour l'envoi d'un SMS
def send_sms(phone_number, message):
    # Dans cette fonction utiliserait une API comme Twilio ou pushbullet

    # Pour le moment, j'ai une clé d'api pushbullet, mais je crois que c'est limité à 50 sms le mois. L'une des limite c'est que elle utiliise l'application pushbullet sur ton telephone et envoie les sms via ton numéro de téléphone.
    # Mais je crois qu'on peu ruser et créer entre deux à 3 carte sim qui vont taffer à cet effet.

    sendSms(pb,message, phone_number)
    print(f"SMS envoyé à {phone_number}: {message}")
    return True

# Fonction utilitaire pourl'envoi d'un email
def send_email(destination, objet, message):
    send_mail(mail, objet, message, destination) # Importé depuis __init__.py à la racine du projet
    print(f"Email envoyé à {destination} avec le sujet '{objet}': {message}")
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

    # Récupérer les options pour les filtres
    promotions = [promotion.value for promotion in PromotionEnum]
    specialites = [specialite.value for specialite in SpecialiteEnum]
    statuts = [statut.value for statut in StatutProfessionnelEnum]

    return render_template('admin/dashboard.html',
                           profiles=profiles,
                           promotions=promotions,
                           specialites=specialites,
                           statuts=statuts)

@admin_bp.route('/search', methods=['POST'])
@login_required
def search():
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': "Vous n'avez pas les droits d'accès à cette action."}), 403

    # Récupérer les paramètres de recherche
    search_query = request.form.get('query', '')
    promotion_filter = request.form.get('promotion', '')
    specialite_filter = request.form.get('specialite', '')
    statut_filter = request.form.get('statut', '')

    # Construire la requête de base
    query = UserProfile.query

    # Appliquer les filtres
    if search_query:
        query = query.filter(
            or_(
                UserProfile.nom_prenoms.ilike(f'%{search_query}%'),
                UserProfile.email.ilike(f'%{search_query}%'),
                UserProfile.structure.ilike(f'%{search_query}%'),
                UserProfile.fonction.ilike(f'%{search_query}%'),
                UserProfile.localite_residence.ilike(f'%{search_query}%'),
                UserProfile.biographie.ilike(f'%{search_query}%')
            )
        )

    if promotion_filter:
        # Convertir la valeur du filtre en enum
        try:
            promotion_enum = PromotionEnum(promotion_filter)
            query = query.filter(UserProfile.promotion == promotion_enum)
        except ValueError:
            # Si la conversion échoue, ignorer ce filtre
            pass

    if specialite_filter:
        # Convertir la valeur du filtre en enum
        try:
            specialite_enum = SpecialiteEnum(specialite_filter)
            query = query.filter(UserProfile.specialite == specialite_enum)
        except ValueError:
            # Si la conversion échoue, ignorer ce filtre
            pass

    if statut_filter:
        # Convertir la valeur du filtre en enum
        try:
            statut_enum = StatutProfessionnelEnum(statut_filter)
            query = query.filter(UserProfile.statut_professionnel == statut_enum)
        except ValueError:
            # Si la conversion échoue, ignorer ce filtre
            pass

    # Exécuter la requête
    profiles = query.all()

    # Préparer les résultats pour le rendu AJAX
    results = []
    for profile in profiles:
        results.append({
            'id': profile.user_id,
            'nom_prenoms': profile.nom_prenoms,
            'email': profile.email,
            'promotion': profile.promotion.value if profile.promotion else '',
            'specialite': profile.specialite.value if profile.specialite else '',
            'structure': profile.structure or '',
            'fonction': profile.fonction or '',
            'statut_professionnel': profile.statut_professionnel.value if profile.statut_professionnel else '',
            'photo_url': f'/static/uploads/photos/{profile.photo_filename}' if profile.photo_filename else '/static/assets/images/avatars/avatar-2.jpg',
        })

    return jsonify({'success': True, 'profiles': results})

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

        Votre compte a été créé dans l'annuaire ENSA.

        Voici vos identifiants de connexion:
        Email: {email}
        Mot de passe: {password}

        Nous vous invitons à vous connecter et à compléter votre profil ainsi qu'à réinitialiser votre mot de passe.

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

@admin_bp.route('/import-members', methods=['GET', 'POST'])
@login_required
def import_members():
    # Vérifier si l'utilisateur est un administrateur
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'accès à cette page.", 'danger')
        return redirect(url_for('index.index'))

    results = {
        'success': 0,
        'errors': [],
        'total': 0
    }

    if request.method == 'POST':
        # Vérifier si un fichier a été téléchargé
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)

        # Vérifier l'extension du fichier (CSV ou Excel)
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            flash('Format de fichier non supporté. Veuillez télécharger un fichier CSV ou Excel (.xlsx, .xls)', 'danger')
            return redirect(request.url)

        try:
            # Lecture du fichier selon son format
            if file.filename.endswith('.csv'):
                # Lire le fichier CSV
                stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
                reader = csv.DictReader(stream)
                data = [row for row in reader]
            else:
                # Lire le fichier Excel
                df = pd.read_excel(file)
                data = df.to_dict('records')

            results['total'] = len(data)

            # Champs requis et correspondance
            required_fields = ['email', 'nom_prenoms']

            # Traitement de chaque ligne
            for index, row in enumerate(data, start=1):
                try:
                    # Vérifier les champs requis
                    missing_fields = [field for field in required_fields if field not in row or not row[field]]
                    if missing_fields:
                        results['errors'].append(f"Ligne {index}: champs manquants: {', '.join(missing_fields)}")
                        continue

                    # Vérifier si l'utilisateur existe déjà
                    email = row['email'].strip()
                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user:
                        results['errors'].append(f"Ligne {index}: Un utilisateur avec l'email {email} existe déjà.")
                        continue

                    # Créer un nouvel utilisateur
                    password = generate_password()
                    new_user = User(email=email, role=RoleEnum.USER)
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.flush()  # Pour obtenir l'ID de l'utilisateur

                    # Créer un profil pour l'utilisateur
                    new_profile = UserProfile(
                        user_id=new_user.id,
                        nom_prenoms=row['nom_prenoms'].strip(),
                        email=email
                    )

                    # Traiter les champs optionnels
                    if 'promotion' in row and row['promotion']:
                        try:
                            promotion_value = row['promotion'].strip()
                            # Vérifier si la valeur correspond à une énumération
                            for enum_value in PromotionEnum:
                                if enum_value.value == promotion_value:
                                    new_profile.promotion = enum_value
                                    break
                        except Exception as e:
                            print(f"Erreur lors du traitement de la promotion: {e}")

                    if 'specialite' in row and row['specialite']:
                        try:
                            specialite_value = row['specialite'].strip()
                            for enum_value in SpecialiteEnum:
                                if enum_value.value == specialite_value:
                                    new_profile.specialite = enum_value
                                    break
                        except Exception as e:
                            print(f"Erreur lors du traitement de la spécialité: {e}")

                    if 'statut_professionnel' in row and row['statut_professionnel']:
                        try:
                            statut_value = row['statut_professionnel'].strip()
                            for enum_value in StatutProfessionnelEnum:
                                if enum_value.value == statut_value:
                                    new_profile.statut_professionnel = enum_value
                                    break
                        except Exception as e:
                            print(f"Erreur lors du traitement du statut professionnel: {e}")

                    # Autres champs simples
                    field_mapping = {
                        'structure': 'structure',
                        'fonction': 'fonction',
                        'localite_residence': 'localite_residence',
                        'numero_whatsapp': 'numero_whatsapp',
                        'autres_numeros': 'autres_numeros',
                        'compte_linkedin': 'compte_linkedin',
                        'biographie': 'biographie'
                    }

                    for csv_field, model_field in field_mapping.items():
                        if csv_field in row and row[csv_field]:
                            setattr(new_profile, model_field, row[csv_field].strip())

                    # Champ booléen
                    if 'is_mentor_available' in row:
                        value = row['is_mentor_available']
                        if isinstance(value, bool):
                            new_profile.is_mentor_available = value
                        elif isinstance(value, str):
                            value = value.lower().strip()
                            new_profile.is_mentor_available = value in ('true', 'oui', 'yes', '1')

                    db.session.add(new_profile)

                    # Envoyer un email avec les identifiants
                    email_subject = "Bienvenue dans l'annuaire des alumni"
                    email_message = f"""
                    Bonjour {new_profile.nom_prenoms},

                    Votre compte a été créé dans l'annuaire ENSA.

                    Voici vos identifiants de connexion:
                    Email: {email}
                    Mot de passe: {password}

                    Nous vous invitons à vous connecter et à compléter votre profil ainsi qu'à réinitialiser votre mot de passe.

                    Cordialement,
                    L'équipe de l'annuaire
                    """

                    send_email(email, email_subject, email_message)

                    # Envoyer un SMS si un numéro WhatsApp est fourni
                    if new_profile.numero_whatsapp:
                        sms_message = f"Bienvenue dans l'annuaire des alumni! Vos identifiants: Email: {email}, Mot de passe: {password}"
                        send_sms(new_profile.numero_whatsapp, sms_message)

                    results['success'] += 1

                except Exception as e:
                    results['errors'].append(f"Ligne {index}: {str(e)}")
                    db.session.rollback()

            # Valider les transactions réussies
            if results['success'] > 0:
                db.session.commit()
                flash(f"{results['success']} membre(s) importé(s) avec succès. {len(results['errors'])} erreur(s).", 'success')
            else:
                flash("Aucun membre n'a été importé. Veuillez vérifier les erreurs.", 'danger')

        except Exception as e:
            results['errors'].append(f"Erreur lors du traitement du fichier: {str(e)}")
            flash(f"Erreur lors du traitement du fichier: {str(e)}", 'danger')

    # Liste des champs d'énumération pour le template
    promotions = [promotion.value for promotion in PromotionEnum]
    specialites = [specialite.value for specialite in SpecialiteEnum]
    statuts = [statut.value for statut in StatutProfessionnelEnum]

    return render_template('admin/import_members.html',
                           results=results,
                           promotions=promotions,
                           specialites=specialites,
                           statuts=statuts)
