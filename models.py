from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from __init__ import db, login_manager

from enum_list import *
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    messages = db.relationship("Message", back_populates="user")
    likes = db.relationship("Like", back_populates="user")

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
        return self.role == RoleEnum.ADMIN or self.role == RoleEnum.SUPER_ADMIN

    @property
    def is_super_admin(self):
        return self.role == RoleEnum.SUPER_ADMIN

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




class Discussion(db.Model):
    __tablename__ = 'discussions'

    id_discussion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sujet = db.Column(db.String, nullable=False)
    messages = db.relationship("Message", back_populates="discussion")


class Message(db.Model):
    __tablename__ = 'messages'

    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    id_discussion = db.Column(db.Integer, db.ForeignKey('discussions.id_discussion'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_ecriture = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    user = db.relationship("User", back_populates="messages")
    discussion = db.relationship("Discussion", back_populates="messages")

class Like(db.Model):
    __tablename__ = 'likes'

    user_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    id_message = db.Column(db.Integer, db.ForeignKey('messages.id_message'), primary_key=True)

    user = db.relationship("User", back_populates="likes")
    message = db.relationship("Message")
