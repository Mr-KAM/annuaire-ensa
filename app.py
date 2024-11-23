#=======================================================================
#IMPORTATION DES PACKAGES ET MODULES

from flask import Flask, render_template, request, jsonify
#----------------------------------
#Importation des routes dépuis le dossier routes


#=======================================================================
#CREATION DE L'APP
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.db' # Configure the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable the feature of flask_sqlalchemy that signals the application everytime a change is about to be made in the database
from models import *




from routes.index import *
from routes.annuaire import*


#=======================================================================
#PROGRAMME PRINCIPAL
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
