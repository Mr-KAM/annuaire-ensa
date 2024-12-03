from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CheckConstraint
from app import app
from enum import Enum


db = SQLAlchemy(app)
Base = declarative_base()


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    horodateur = Column(DateTime, nullable=False)
    nom_prenoms = Column(String(50), nullable=False)
    prenoms = Column(String(255), nullable=False)
    promotion_ensa_esa = Column(Enum, nullable=True)
    specialite = Column(Enum, nullable=True)
    structure_actuelle = Column(String(255), nullable=True)
    fonction_actuelle = Column(String(100), nullable=True)
    localite_residence = Column(String(100), nullable=True)
    numero_whatsapp = Column(String(15), nullable=True)
    autres_numeros = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    compte_linkedin = Column(String(255), nullable=True)
    biographie = Column(Text, nullable=True)
    photo = Column(String(255), nullable=True)
    adresse_email = Column(String(255), nullable=True)
    is_mentor_available = Column(bool, nullable=True, default=False)
    statut_professionnel = Column(Enum, nullable=True)
    role = Column(String(20), nullable=False, default="user")



    __table_args__ = (
        CheckConstraint("LENGTH(numero_whatsapp) >= 10", name="check_whatsapp_length"),
    )

    def __repr__(self):
        return f"<UserProfile(nom_prenoms='{self.nom_prenoms}', email='{self.email}')>"
