"""
API d'exposition - Neovolt Grid+ (Volet Data Engineering).

Met a disposition les donnees nettoyees pour les autres volets :
  - Data Analyst    -> /consommation/agregee (alimente les tableaux de bord)
  - Data Scientist  -> /releves, /meteo (features pour les modeles)
  - Gouvernance/CP  -> /qualite (metriques de qualite de la derniere ingestion)
  - Exploitation    -> /incidents

Lancer :  uvicorn neovolt.api:app --reload --port 8000
Doc auto :  http://localhost:8000/docs
"""
from typing import Optional
from pathlib import Path
from datetime import datetime
import csv

from fastapi import FastAPI, Depends, Query, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .db import (engine, SessionLocal, Client, Compteur, ReleveConso, Meteo,
                 Incident, Fraude, QualityReport)


def _periode_expr(col, granularite):
    """Troncature de date portable : to_char sous PostgreSQL, strftime sous SQLite."""
    if engine.dialect.name == "postgresql":
        fmt = "YYYY-MM" if granularite == "mois" else "YYYY-MM-DD"
        return func.to_char(col, fmt)
    fmt = "%Y-%m" if granularite == "mois" else "%Y-%m-%d"
    return func.strftime(fmt, col)

app = FastAPI(
    title="Neovolt Grid+ - Data API",
    version="0.1.0",
    description="Exposition des donnees de consommation nettoyees (prototype).",
)

LOG_FILE = Path(__file__).resolve().parents[2] / "Volet_E_cybersecurite" / "data" / "logs_api_volet_d.csv"


def write_security_log(
    utilisateur: str,
    source_ip: str,
    systeme: str,
    type_evenement: str,
    resultat: str
):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "horodatage",
                "utilisateur",
                "source_ip",
                "systeme",
                "type_evenement",
                "resultat"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            utilisateur,
            source_ip,
            systeme,
            type_evenement,
            resultat
        ])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health(request: Request):
    write_security_log(
        utilisateur="api_user",
        source_ip=request.client.host,
        systeme="api_data_engineering",
        type_evenement="appel_health",
        resultat="succes"
    )

    return {"status": "ok"}


@app.get("/compteurs/{id_pdl}")
def compteur(id_pdl: str, request: Request, db: Session = Depends(get_db)):
    write_security_log(
        utilisateur="api_user",
        source_ip=request.client.host,
        systeme="api_data_engineering",
        type_evenement="consultation_compteur",
        resultat="succes"
    )
    c = db.get(Compteur, id_pdl)
    if not c:
        raise HTTPException(404, "PDL inconnu")
    return {k: getattr(c, k) for k in c.__table__.columns.keys()}


@app.get("/releves")
def releves(
    request: Request,
    id_pdl: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    qualite: Optional[str] = Query(None, description="filtrer par flag qualite"),
    limit: int = Query(1000, le=50000),
    db: Session = Depends(get_db),
):
    write_security_log(
    utilisateur="api_user",
    source_ip=request.client.host,
    systeme="api_data_engineering",
    type_evenement="consultation_releves",
    resultat="succes"
    )

    q = select(ReleveConso)
    if id_pdl:
        q = q.where(ReleveConso.id_pdl == id_pdl)
    if date_debut:
        q = q.where(ReleveConso.date_releve >= date_debut)
    if date_fin:
        q = q.where(ReleveConso.date_releve <= date_fin)
    if qualite:
        q = q.where(ReleveConso.qualite == qualite)
    rows = db.execute(q.limit(limit)).scalars().all()
    return [
        {"id_pdl": r.id_pdl, "date": str(r.date_releve),
         "consommation_kwh": r.consommation_kwh, "zone": r.zone, "qualite": r.qualite}
        for r in rows
    ]


@app.get("/consommation/agregee")
def conso_agregee(
    request: Request,
    zone: Optional[str] = None,
    granularite: str = Query("mois", pattern="^(jour|mois)$"),
    db: Session = Depends(get_db),
):
    write_security_log(
    utilisateur="api_user",
    source_ip=request.client.host,
    systeme="api_data_engineering",
    type_evenement="consultation_consommation_agregee",
    resultat="succes"
    )
    """Consommation agregee pour les tableaux de bord (relevs 'ok' uniquement)."""
    fmt = "%Y-%m" if granularite == "mois" else "%Y-%m-%d"
    periode = _periode_expr(ReleveConso.date_releve, granularite).label("periode")
    q = (select(periode, ReleveConso.zone,
                func.sum(ReleveConso.consommation_kwh).label("conso_kwh"),
                func.count().label("nb_releves"))
         .where(ReleveConso.qualite == "ok")
         .group_by("periode", ReleveConso.zone)
         .order_by("periode"))
    if zone:
        q = q.where(ReleveConso.zone == zone)
    return [dict(r._mapping) for r in db.execute(q).all()]


@app.get("/meteo")
def meteo(request: Request, zone: Optional[str] = None, date_debut: Optional[str] = None, date_fin: Optional[str] = None, limit: int = Query(2000, le=20000), db: Session = Depends(get_db)):
    write_security_log(
        utilisateur="api_user",
        source_ip=request.client.host,
        systeme="api_data_engineering",
        type_evenement="consultation_meteo",
        resultat="succes"
    )

    q = select(Meteo)
    if zone:
        q = q.where(Meteo.zone == zone)
    if date_debut:
        q = q.where(Meteo.date_meteo >= date_debut)
    if date_fin:
        q = q.where(Meteo.date_meteo <= date_fin)
    rows = db.execute(q.limit(limit)).scalars().all()
    return [{"date": str(r.date_meteo), "zone": r.zone,
             "temp_moyenne_c": r.temp_moyenne_c} for r in rows]


@app.get("/incidents")
def incidents(request: Request, zone: Optional[str] = None, db: Session = Depends(get_db)):

    write_security_log(
        utilisateur="api_user",
        source_ip=request.client.host,
        systeme="api_data_engineering",
        type_evenement="consultation_incidents",
        resultat="succes"
    )

    q = select(Incident)
    if zone:
        q = q.where(Incident.zone == zone)
    rows = db.execute(q).scalars().all()
    return [{"id_incident": r.id_incident, "date_debut": str(r.date_debut),
             "zone": r.zone, "type": r.type, "cause": r.cause,
             "nb_pdl_impactes": r.nb_pdl_impactes} for r in rows]


@app.get("/qualite")
def qualite(request: Request, db: Session = Depends(get_db)):

    write_security_log(
        utilisateur="api_user",
        source_ip=request.client.host,
        systeme="api_data_engineering",
        type_evenement="consultation_qualite",
        resultat="succes"
    )

    """Metriques de qualite de la derniere ingestion (pour la gouvernance)."""
    rows = db.execute(select(QualityReport).order_by(QualityReport.id)).scalars().all()
    return [{"table": r.table_cible, "metrique": r.metrique, "valeur": r.valeur}
            for r in rows]
