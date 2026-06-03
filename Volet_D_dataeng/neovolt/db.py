"""
Modele de donnees et connexion - Neovolt Grid+ (Volet Data Engineering).

Source de verite unique du schema : les memes tables servent au pipeline
d'ingestion ET a l'API. Compatible PostgreSQL (production / docker-compose)
et SQLite (test local rapide), via la variable DATABASE_URL.
"""
import os
from sqlalchemy import (create_engine, Column, String, Float, Integer, Date,
                        DateTime, ForeignKey, Index)
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL en prod, SQLite par defaut pour un test local sans conteneur.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "neovolt.db"),
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
Base = declarative_base()


class Client(Base):
    __tablename__ = "dim_client"
    id_client = Column(String, primary_key=True)
    segment = Column(String)
    commune = Column(String)
    code_postal = Column(String)
    date_entree = Column(Date)
    nb_personnes_foyer = Column(Integer)   # null attendu hors residentiel
    surface_m2 = Column(Float)             # null attendu hors residentiel


class Compteur(Base):
    __tablename__ = "dim_compteur"
    id_pdl = Column(String, primary_key=True)
    id_client = Column(String, ForeignKey("dim_client.id_client"))
    zone = Column(String)
    type_client = Column(String)
    puissance_souscrite_kva = Column(Float)
    type_chauffage = Column(String)
    type_compteur = Column(String)
    date_pose = Column(Date)
    statut = Column(String)


class ReleveConso(Base):
    __tablename__ = "fait_releve_conso"
    id_pdl = Column(String, ForeignKey("dim_compteur.id_pdl"), primary_key=True)
    date_releve = Column(Date, primary_key=True)
    consommation_kwh = Column(Float)        # null si manquant ou negatif rejete
    zone = Column(String)
    qualite = Column(String)                # ok | manquant | negatif | suspect_haut


class Meteo(Base):
    __tablename__ = "dim_meteo"
    date_meteo = Column(Date, primary_key=True)
    zone = Column(String, primary_key=True)
    temp_moyenne_c = Column(Float)
    temp_min_c = Column(Float)
    temp_max_c = Column(Float)


class Incident(Base):
    __tablename__ = "fait_incident"
    id_incident = Column(String, primary_key=True)
    date_debut = Column(DateTime)
    duree_minutes = Column(Integer)
    zone = Column(String)
    type = Column(String)
    nb_pdl_impactes = Column(Integer)
    cause = Column(String)


class Fraude(Base):
    __tablename__ = "fait_fraude_confirmee"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_pdl = Column(String, ForeignKey("dim_compteur.id_pdl"))
    date_detection = Column(Date)
    type_fraude = Column(String)
    statut = Column(String)


class QualityReport(Base):
    __tablename__ = "ingestion_qualite"
    id = Column(Integer, primary_key=True, autoincrement=True)
    horodatage = Column(DateTime)
    table_cible = Column(String)
    metrique = Column(String)
    valeur = Column(Float)


# Index utiles aux requetes des autres volets (analyse, modeles, dashboards)
Index("ix_releve_date", ReleveConso.date_releve)
Index("ix_releve_zone", ReleveConso.zone)
Index("ix_meteo_zone_date", Meteo.zone, Meteo.date_meteo)


def init_db(drop=False):
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
