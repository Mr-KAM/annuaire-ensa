from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from __init__ import db
from models import UserProfile, PromotionEnum, SpecialiteEnum, StatutProfessionnelEnum
from sqlalchemy import or_

annuaire_bp = Blueprint('annuaire', __name__, url_prefix='/annuaire')

@annuaire_bp.route('/')
@login_required
def index():
    # Récupérer tous les profils
    profiles = UserProfile.query.all()

    # Récupérer les options pour les filtres
    promotions = [promotion.value for promotion in PromotionEnum]
    specialites = [specialite.value for specialite in SpecialiteEnum]
    statuts = [statut.value for statut in StatutProfessionnelEnum]

    return render_template('annuaire/index.html',
                          profiles=profiles,
                          promotions=promotions,
                          specialites=specialites,
                          statuts=statuts)

@annuaire_bp.route('/search', methods=['POST'])
@login_required
def search():
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
                UserProfile.structure.ilike(f'%{search_query}%'),
                UserProfile.fonction.ilike(f'%{search_query}%'),
                UserProfile.localite_residence.ilike(f'%{search_query}%'),
                UserProfile.biographie.ilike(f'%{search_query}%')
            )
        )

    if promotion_filter:
        query = query.filter(UserProfile.promotion == promotion_filter)

    if specialite_filter:
        query = query.filter(UserProfile.specialite == specialite_filter)

    if statut_filter:
        query = query.filter(UserProfile.statut_professionnel == statut_filter)

    # Exécuter la requête
    profiles = query.all()

    # Préparer les résultats pour le rendu AJAX
    results = []
    for profile in profiles:
        results.append({
            'id': profile.user_id,
            'nom_prenoms': profile.nom_prenoms,
            'promotion': profile.promotion.value if profile.promotion else '',
            'specialite': profile.specialite.value if profile.specialite else '',
            'structure': profile.structure,
            'fonction': profile.fonction,
            'photo_url': f'/static/uploads/photos/{profile.photo_filename}' if profile.photo_filename else '/static/assets/images/avatars/avatar-2.jpg',
            'profile_url': f'/profile/user/{profile.user_id}'
        })

    return jsonify({'success': True, 'profiles': results})
