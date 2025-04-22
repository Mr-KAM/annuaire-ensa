from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from __init__ import db, login_manager
import enum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PromotionEnum(enum.Enum):
    ENSA_1 = "1er PROMOTION"
    ENSA_2 = "2ème PROMOTION"
    ENSA_3 = "3ème PROMOTION"
    ENSA_4 = "4ème PROMOTION"
    ENSA_5 = "5ème PROMOTION"
    ENSA_6 = "6ème PROMOTION"
    ENSA_7 = "7ème PROMOTION"
    ENSA_8 = "8ème PROMOTION"
    ENSA_9 = "9ème PROMOTION"
    ENSA_10 = "10ème PROMOTION"
    ENSA_11 = "11ème PROMOTION"
    ENSA_12 = "12ème PROMOTION"
    ENSA_13 = "13ème PROMOTION"
    ENSA_14 = "14ème PROMOTION"
    ENSA_15 = "15ème PROMOTION"
    ENSA_16 = "16ème PROMOTION"
    ENSA_17 = "17ème PROMOTION"
    ENSA_18 = "18ème PROMOTION"
    ENSA_19 = "19ème PROMOTION"
    ENSA_20 = "20ème PROMOTION"
    ENSA_21 = "21ème PROMOTION"
    ENSA_22 = "22ème PROMOTION"
    ENSA_23 = "23ème PROMOTION"
    ENSA_24 = "24ème PROMOTION"
    ENSA_25 = "25ème PROMOTION"
    ENSA_26 = "26ème PROMOTION"
    ENSA_27 = "27ème PROMOTION"
    ENSA_28 = "28ème PROMOTION"
    ENSA_29 = "29ème PROMOTION"
    ENSA_30 = "30ème PROMOTION"
    ENSA_31 = "31ème PROMOTION"
    ENSA_32 = "32ème PROMOTION"
    ENSA_33 = "33ème PROMOTION"
    ENSA_34 = "34ème PROMOTION"
    ENSA_35 = "35ème PROMOTION"
    ENSA_36 = "36ème PROMOTION"
    ENSA_37 = "37ème PROMOTION"
    ENSA_38 = "38ème PROMOTION"
    ENSA_39 = "39ème PROMOTION"
    ENSA_40 = "40ème PROMOTION"
    ENSA_41 = "41ème PROMOTION"
    ENSA_42 = "42ème PROMOTION"
    ENSA_43 = "43ème PROMOTION"
    ENSA_44 = "44ème PROMOTION"
    ENSA_45 = "45ème PROMOTION"
    ENSA_46 = "46ème PROMOTION"
    ENSA_47 = "47ème PROMOTION"
    ENSA_48 = "48ème PROMOTION"
    ENSA_49 = "49ème PROMOTION"
    ENSA_50 = "50ème PROMOTION"
    ENSA_51 = "51ème PROMOTION"
    ENSA_52 = "52ème PROMOTION"
    ENSA_53 = "53ème PROMOTION"
    ENSA_54 = "54ème PROMOTION"
    ENSA_55 = "55ème PROMOTION"
    ENSA_56 = "56ème PROMOTION"
    ENSA_57 = "57ème PROMOTION"
    ENSA_58 = "58ème PROMOTION"
    ENSA_59 = "59ème PROMOTION"
    ENSA_60 = "60ème PROMOTION"
    ENSA_61 = "61ème PROMOTION"
    ENSA_62 = "62ème PROMOTION"
    ENSA_63 = "63ème PROMOTION"
    ENSA_64 = "64ème PROMOTION"
    ENSA_65 = "65ème PROMOTION"
    ENSA_66 = "66ème PROMOTION"
    ENSA_67 = "67ème PROMOTION"
    ENSA_68 = "68ème PROMOTION"
    ENSA_69 = "69ème PROMOTION"
    ENSA_70 = "70ème PROMOTION"
    ENSA_71 = "71ème PROMOTION"
    ENSA_72 = "72ème PROMOTION"
    ENSA_73 = "73ème PROMOTION"
    ENSA_74 = "74ème PROMOTION"
    ENSA_75 = "75ème PROMOTION"
    ENSA_76 = "76ème PROMOTION"
    ENSA_77 = "77ème PROMOTION"
    ENSA_78 = "78ème PROMOTION"
    ENSA_79 = "79ème PROMOTION"
    ENSA_80 = "80ème PROMOTION"
    ENSA_81 = "81ème PROMOTION"
    ENSA_82 = "82ème PROMOTION"
    ENSA_83 = "83ème PROMOTION"
    ENSA_84 = "84ème PROMOTION"
    ENSA_85 = "85ème PROMOTION"
    ENSA_86 = "86ème PROMOTION"
    ENSA_87 = "87ème PROMOTION"
    ENSA_88 = "88ème PROMOTION"
    ENSA_89 = "89ème PROMOTION"
    ENSA_90 = "90ème PROMOTION"
    ENSA_91 = "91ème PROMOTION"
    ENSA_92 = "92ème PROMOTION"
    ENSA_93 = "93ème PROMOTION"
    ENSA_94 = "94ème PROMOTION"
    ENSA_95 = "95ème PROMOTION"
    ENSA_96 = "96ème PROMOTION"
    ENSA_97 = "97ème PROMOTION"
    ENSA_98 = "98ème PROMOTION"
    ENSA_99 = "99ème PROMOTION"
    ENSA_100 = "100ème PROMOTION"
    ENSA_101 = "101ème PROMOTION"
    ENSA_102 = "102ème PROMOTION"
    ENSA_103 = "103ème PROMOTION"
    ENSA_104 = "104ème PROMOTION"
    ENSA_105 = "105ème PROMOTION"
    ENSA_106 = "106ème PROMOTION"
    ENSA_107 = "107ème PROMOTION"
    ENSA_108 = "108ème PROMOTION"
    ENSA_109 = "109ème PROMOTION"
    ENSA_110 = "110ème PROMOTION"
    ENSA_111 = "111ème PROMOTION"
    ENSA_112 = "112ème PROMOTION"
    ENSA_113 = "113ème PROMOTION"
    ENSA_114 = "114ème PROMOTION"
    ENSA_115 = "115ème PROMOTION"
    ENSA_116 = "116ème PROMOTION"
    ENSA_117 = "117ème PROMOTION"
    ENSA_118 = "118ème PROMOTION"
    ENSA_119 = "119ème PROMOTION"
    ENSA_120 = "120ème PROMOTION"
    INDEFINI= "INDEFINIE"

class SpecialiteEnum(enum.Enum):
    AGRO_ECONOMIE = "AGRO ECONOMIE"
    AGRI_BUSINESS = "AGRI-BUSINESS"
    EAUX_FORETS = "EAUX ET FORETS"
    GENIE_RURAL = "GENIE RURAL"
    AGRO_EQUIPEMENT = "AGRO EQUIPEMENT"
    PEDOLOGIE = "PEDOLOGIE"
    AGRO_TIC = "AGRO TIC"
    AGRO_ALIMENTAIRE = "AGRO ALIMENTAIRE"
    AGRO_ENERGIE = "AGRO ENERGIE"
    CCDD = "CHANGEMENT CLIMATIQUE ET DEVELOPPEMENT DURABLE"
    ZOOTECHNIE = "ZOOTECHNIE"
    PRODUCTION_VEGETALE = "PRODUCTION VEGETALE"
    PRODUCTION_ANIMALE = "PRODUCTION ANIMALE"
    DEFENCE_DES_CULTURES = "DEFENSE DES CULTURES"
    INDEFINIE = "INDEFINIE"
class StatutProfessionnelEnum(enum.Enum):
    ETUDIANT = "Étudiant-Cadet en formation"
    EMPLOYE_PUBLIQUE = "Employé de la fonction publique"
    EMPLOYE_PRIVEE = "Employé du secteur privé"
    ENTREPRENEUR = "Entrepreneur"
    FREELANCE = "Freelance"
    RECHERCHE_EMPLOI = "En recherche d'emploi"
    DIPLOME_ETUDIANTS = "Diplômé en poursuite des études"
    RETRAITE = "Retraité"
    AUTRE = "Autre"

class RoleEnum(enum.Enum):
    SUPER_ADMIN = "super_admin"
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
