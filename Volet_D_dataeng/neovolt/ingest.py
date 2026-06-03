"""
Pipeline d'ingestion par lots - Neovolt Grid+ (Volet Data Engineering).

Principe industriel vise : ce script joue le role d'un job batch quotidien
(orchestrable par Airflow / cron) qui ingere les relevs de la veille (J+1),
les nettoie, journalise la qualite, puis charge dans l'entrepot. Ici on charge
l'historique complet fourni ; en production on ne chargerait qu'un delta.

Regles de nettoyage (assumees et defendables) :
- doublons (id_pdl, date) -> on garde le dernier relev
- consommation manquante  -> conservee a NULL, marquee 'manquant'
                             (on n'invente pas de valeur : l'imputation releve
                              du Data Scientist, pas du pipeline)
- consommation negative    -> physiquement impossible -> NULL + 'negatif'
- consommation trop haute  -> seuil PHYSIQUE = puissance_souscrite_kva * 24h
                             (et non un seuil statistique aveugle qui
                              rejetterait a tort les profils industriels)
                             -> valeur conservee mais marquee 'suspect_haut'
- integrite referentielle  -> assuree par les cles etrangeres du schema
"""
import os
import datetime as dt
import pandas as pd
from sqlalchemy import insert
from .db import (engine, SessionLocal, init_db,
                 Client, Compteur, ReleveConso, Meteo, Incident, Fraude,
                 QualityReport)

DATA_DIR = os.getenv("NEOVOLT_DATA_DIR", "./donnees")
_metrics = []


def _log(table, metrique, valeur):
    _metrics.append({"table_cible": table, "metrique": metrique,
                     "valeur": float(valeur)})


def _read(name):
    return pd.read_csv(os.path.join(DATA_DIR, name))


def load_referentiels():
    cli = _read("clients.csv").drop_duplicates(subset=["id_client"])
    cli["date_entree"] = pd.to_datetime(cli["date_entree"], errors="coerce").dt.date
    _log("dim_client", "lignes_chargees", len(cli))
    _log("dim_client", "champs_optionnels_vides", int(cli[["nb_personnes_foyer", "surface_m2"]].isna().sum().sum()))

    comp = _read("compteurs.csv").drop_duplicates(subset=["id_pdl"])
    comp["date_pose"] = pd.to_datetime(comp["date_pose"], errors="coerce").dt.date
    _log("dim_compteur", "lignes_chargees", len(comp))
    return cli, comp


def clean_releves(comp):
    df = _read("releves_consommation.csv")
    brut = len(df)
    _log("fait_releve_conso", "lignes_brutes", brut)

    dups = df.duplicated(subset=["id_pdl", "date"]).sum()
    df = df.drop_duplicates(subset=["id_pdl", "date"], keep="last")
    _log("fait_releve_conso", "doublons_supprimes", dups)

    df["date_releve"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["consommation_kwh"] = pd.to_numeric(df["consommation_kwh"], errors="coerce")

    seuil = comp.set_index("id_pdl")["puissance_souscrite_kva"] * 24.0
    df = df.merge(seuil.rename("seuil_haut"), left_on="id_pdl", right_index=True, how="left")

    c = df["consommation_kwh"]
    df["qualite"] = "ok"
    df.loc[c.isna(), "qualite"] = "manquant"
    neg = c < 0
    df.loc[neg, "qualite"] = "negatif"
    df.loc[neg, "consommation_kwh"] = None
    haut = (c >= 0) & (df["seuil_haut"].notna()) & (c > df["seuil_haut"])
    df.loc[haut, "qualite"] = "suspect_haut"

    for flag in ["manquant", "negatif", "suspect_haut"]:
        _log("fait_releve_conso", f"flag_{flag}", int((df["qualite"] == flag).sum()))
    _log("fait_releve_conso", "lignes_chargees", len(df))
    _log("fait_releve_conso", "taux_ok_pct", round(100 * (df["qualite"] == "ok").mean(), 2))

    return df[["id_pdl", "date_releve", "consommation_kwh", "zone", "qualite"]]


def load_meteo():
    m = _read("meteo.csv").drop_duplicates(subset=["date", "zone"])
    m["date_meteo"] = pd.to_datetime(m["date"], errors="coerce").dt.date
    _log("dim_meteo", "lignes_chargees", len(m))
    return m[["date_meteo", "zone", "temp_moyenne_c", "temp_min_c", "temp_max_c"]]


def load_incidents():
    i = _read("incidents_reseau.csv").drop_duplicates(subset=["id_incident"])
    i["date_debut"] = pd.to_datetime(i["date_debut"], errors="coerce")
    _log("fait_incident", "lignes_chargees", len(i))
    return i[["id_incident", "date_debut", "duree_minutes", "zone", "type", "nb_pdl_impactes", "cause"]]


def load_fraudes():
    f = _read("cas_fraude_confirmes.csv")
    f["date_detection"] = pd.to_datetime(f["date_detection"], errors="coerce").dt.date
    _log("fait_fraude_confirmee", "lignes_chargees", len(f))
    return f[["id_pdl", "date_detection", "type_fraude", "statut"]]


def run(drop=True):
    print(f"[ingest] DATA_DIR={DATA_DIR}  DB={engine.url}")
    init_db(drop=drop)
    cli, comp = load_referentiels()
    rel = clean_releves(comp)
    met = load_meteo()
    inc = load_incidents()
    fra = load_fraudes()

    with engine.begin() as conn:
        cli.to_sql("dim_client", conn, if_exists="append", index=False)
        comp.to_sql("dim_compteur", conn, if_exists="append", index=False)
        met.to_sql("dim_meteo", conn, if_exists="append", index=False)
        inc.to_sql("fait_incident", conn, if_exists="append", index=False)
        fra.to_sql("fait_fraude_confirmee", conn, if_exists="append", index=False)
        rel.to_sql("fait_releve_conso", conn, if_exists="append", index=False,
                   chunksize=10000, method="multi")

    now = dt.datetime.now()
    with SessionLocal() as s:
        s.add_all([QualityReport(horodatage=now, **m) for m in _metrics])
        s.commit()

    print("[ingest] termine. Rapport qualite :")
    for m in _metrics:
        print(f"   - {m['table_cible']:>22} | {m['metrique']:<24} = {m['valeur']:.2f}")


if __name__ == "__main__":
    run()
