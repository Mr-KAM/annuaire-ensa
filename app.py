from __init__ import create_app, db
from models import User, RoleEnum

app = create_app()

# Fonctions utilitaires
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

#=======================================================================
# PROGRAMME PRINCIPAL
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Création d'un admin par défaut si aucun n'existe
        admin = User.query.filter_by(role=RoleEnum.ADMIN).first()
        if not admin:
            admin = User(email='admin@example.com', role=RoleEnum.ADMIN) # Pour les test. Ces identifiants seront rétiré en mode production
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin créé avec succès: admin@example.com / admin123")

    app.run(debug=True)
