# Néovolt Grid+ — Prototype Data Engineering (Volet D)

Pipeline d'ingestion des relevés de consommation, entrepôt de données et API
d'exposition pour les autres volets (analyse, modèles, tableaux de bord).

> Prototype de cadrage : il **fonctionne réellement** sur les données fournies.
> L'architecture cible (montée en charge, HA, temps réel) est décrite dans
> [`architecture.md`](architecture.md).

## Ce que ça fait

1. **Ingestion par lots** des CSV (`neovolt/ingest.py`) — joue le rôle d'un job quotidien J+1.
2. **Nettoyage** ancré sur les défauts réels des données (voir plus bas).
3. **Journal de qualité** écrit en base (pour la gouvernance).
4. **Entrepôt** PostgreSQL (modèle en étoile : `dim_*` / `fait_*`).
5. **API** FastAPI exposant la donnée propre (`neovolt/api.py`).

## Lancer avec Docker (recommandé)

Placer le dossier `donnees/` fourni à la racine du dépôt, puis :

```bash
cp .env.example .env          # ajuster POSTGRES_PASSWORD
docker compose up --build     # démarre la base + l'API
docker compose run --rm ingest   # charge et nettoie les données
```

API disponible sur http://localhost:8000 — documentation interactive sur **/docs**.

## Lancer en local sans Docker (test rapide sur SQLite)

```bash
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./neovolt.db"
export NEOVOLT_DATA_DIR="./donnees"
python -m neovolt.ingest                 # ingestion + rapport qualité
uvicorn neovolt.api:app --port 8000      # API
```

## Règles de nettoyage (assumées, défendables)

| Défaut détecté (données réelles) | Volume | Traitement |
|---|---|---|
| Doublons `(id_pdl, date)` | 1 286 | suppression, on garde le dernier |
| Consommation manquante | 6 838 | conservée à `NULL`, marquée `manquant` (pas d'invention) |
| Consommation négative | 1 032 | impossible → `NULL` + `negatif` |
| Valeur trop haute | 549 | seuil **physique** `puissance_kva × 24h` → `suspect_haut` |

> Le seuil physique évite de rejeter à tort les profils industriels (un seuil
> statistique aveugle en aurait écarté ~47 000). L'imputation des valeurs
> manquantes est laissée au Data Scientist : le pipeline ne fabrique pas de donnée.

## Endpoints principaux

| Méthode | Route | Pour qui |
|---|---|---|
| GET | `/health` | supervision |
| GET | `/compteurs/{id_pdl}` | tous |
| GET | `/releves?id_pdl=&date_debut=&date_fin=&qualite=` | Data Scientist |
| GET | `/consommation/agregee?zone=&granularite=jour\|mois` | Data Analyst / dashboards |
| GET | `/meteo?zone=&date_debut=&date_fin=` | Data Scientist |
| GET | `/incidents?zone=` | Exploitation |
| GET | `/qualite` | Gouvernance / Chef de projet |

## Comment ça s'intègre aux autres volets

- **Data Analyst** branche Power BI / Python sur `/consommation/agregee`.
- **Data Scientist** récupère features via `/releves` + `/meteo`.
- **Cybersécurité** auditera cette API (surface d'attaque) ; les accès seront à authentifier (piste : OAuth2/JWT — non implémenté dans le prototype).
- **Chef de projet / gouvernance** suit la qualité via `/qualite`.

## Limites assumées (prototype)

- Pas d'authentification sur l'API (à ajouter avant toute mise en service — voir volet Cyber).
- Chargement complet (full refresh) ; en production, chargement incrémental (delta J+1).
- Partitionnement / HA / temps réel : conçus mais non déployés ici.
