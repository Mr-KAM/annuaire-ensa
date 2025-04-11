from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from __init__ import db, login_manager
import enum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PromotionEnum(enum.Enum):
    ESA_2010 = "ESA 2010"
    ESA_2011 = "ESA 2011"
    ESA_2012 = "ESA 2012"
    ESA_2013 = "ESA 2013"
    ESA_2014 = "ESA 2014"
    ESA_2015 = "ESA 2015"
    ENSA_2016 = "ENSA 2016"
    ENSA_2017 = "ENSA 2017"
    ENSA_2018 = "ENSA 2018"
    ENSA_2019 = "ENSA 2019"
    ENSA_2020 = "ENSA 2020"
    ENSA_2021 = "ENSA 2021"
    ENSA_2022 = "ENSA 2022"
    ENSA_2023 = "ENSA 2023"
    ENSA_2024 = "ENSA 2024"

class SpecialiteEnum(enum.Enum):
    GENIE_CIVIL = "Génie Civil"
    GENIE_ELECTRIQUE = "Génie Électrique"
    GENIE_MECANIQUE = "Génie Mécanique"
    GENIE_INFORMATIQUE = "Génie Informatique"
    GENIE_INDUSTRIEL = "Génie Industriel"
    GENIE_PROCEDES = "Génie des Procédés"
    AUTRE = "Autre"

class StatutProfessionnelEnum(enum.Enum):
    ETUDIANT = "Étudiant"
    EMPLOYE = "Employé"
    ENTREPRENEUR = "Entrepreneur"
    FREELANCE = "Freelance"
    RECHERCHE_EMPLOI = "En recherche d'emploi"
    AUTRE = "Autre"

class RoleEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Informations personnelles
    nom_prenoms = Column(String(100), nullable=False)
    promotion = Column(SQLEnum(PromotionEnum), nullable=True)
    specialite = Column(SQLEnum(SpecialiteEnum), nullable=True)
    structure = Column(String(255), nullable=True)  # Employeur
    fonction = Column(String(100), nullable=True)
    localite_residence = Column(String(100), nullable=True)
    numero_whatsapp = Column(String(20), nullable=True)
    autres_numeros = Column(String(100), nullable=True)
    email = Column(String(255), nullable=False)
    compte_linkedin = Column(String(255), nullable=True)
    biographie = Column(Text, nullable=True)

    # Fichiers
    photo_filename = Column(String(255), nullable=True)
    cv_filename = Column(String(255), nullable=True)

    # Statut
    statut_professionnel = Column(SQLEnum(StatutProfessionnelEnum), nullable=True)
    is_mentor_available = Column(Boolean, nullable=True, default=False)

    # Relation avec User
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    __table_args__ = (
        db.CheckConstraint("LENGTH(numero_whatsapp) >= 10", name="check_whatsapp_length"),
    )

    def __repr__(self):
        return f"<UserProfile(nom_prenoms='{self.nom_prenoms}', email='{self.email}')>"
