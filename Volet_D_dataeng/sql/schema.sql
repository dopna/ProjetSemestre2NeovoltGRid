-- =====================================================================
-- Neovolt Grid+ : schema de reference (PostgreSQL)  -  Volet Data Engineering
-- ---------------------------------------------------------------------
-- Note : en execution, les tables sont creees automatiquement par
-- SQLAlchemy (neovolt/db.py). Ce fichier documente la CIBLE de production,
-- notamment le PARTITIONNEMENT, non gere par le prototype.
-- =====================================================================

-- Referentiels (dimensions) ------------------------------------------
CREATE TABLE dim_client (
    id_client          TEXT PRIMARY KEY,
    segment            TEXT,
    commune            TEXT,
    code_postal        TEXT,
    date_entree        DATE,
    nb_personnes_foyer INTEGER,   -- NULL attendu hors residentiel
    surface_m2         REAL        -- NULL attendu hors residentiel
);

CREATE TABLE dim_compteur (
    id_pdl                  TEXT PRIMARY KEY,
    id_client               TEXT REFERENCES dim_client(id_client),
    zone                    TEXT,
    type_client             TEXT,
    puissance_souscrite_kva REAL,
    type_chauffage          TEXT,
    type_compteur           TEXT,
    date_pose               DATE,
    statut                  TEXT
);

CREATE TABLE dim_meteo (
    date_meteo     DATE,
    zone           TEXT,
    temp_moyenne_c REAL,
    temp_min_c     REAL,
    temp_max_c     REAL,
    PRIMARY KEY (date_meteo, zone)
);

-- Faits ---------------------------------------------------------------
-- En production, table partitionnee par mois (volumetrie : 600 000 PDL
-- x relevs quotidiens -> ~220 M lignes / an). Le partitionnement permet
-- d'elaguer les partitions anciennes (politique de retention 3 ans) et
-- d'accelerer les requetes par periode.
--
--   CREATE TABLE fait_releve_conso (...) PARTITION BY RANGE (date_releve);
--   CREATE TABLE fait_releve_conso_2024_01 PARTITION OF fait_releve_conso
--       FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
--
CREATE TABLE fait_releve_conso (
    id_pdl           TEXT REFERENCES dim_compteur(id_pdl),
    date_releve      DATE,
    consommation_kwh REAL,         -- NULL si manquant ou negatif rejete
    zone             TEXT,
    qualite          TEXT,         -- ok | manquant | negatif | suspect_haut
    PRIMARY KEY (id_pdl, date_releve)
);
CREATE INDEX ix_releve_date ON fait_releve_conso (date_releve);
CREATE INDEX ix_releve_zone ON fait_releve_conso (zone);

CREATE TABLE fait_incident (
    id_incident     TEXT PRIMARY KEY,
    date_debut      TIMESTAMP,
    duree_minutes   INTEGER,
    zone            TEXT,
    type            TEXT,
    nb_pdl_impactes INTEGER,
    cause           TEXT
);

CREATE TABLE fait_fraude_confirmee (
    id             SERIAL PRIMARY KEY,
    id_pdl         TEXT REFERENCES dim_compteur(id_pdl),
    date_detection DATE,
    type_fraude    TEXT,
    statut         TEXT
);

-- Journal de qualite d'ingestion (pour la gouvernance) ----------------
CREATE TABLE ingestion_qualite (
    id          SERIAL PRIMARY KEY,
    horodatage  TIMESTAMP,
    table_cible TEXT,
    metrique    TEXT,
    valeur      REAL
);
