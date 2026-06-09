# Projet Semestre 2 – NÉOVOLT GRID+

## Contexte

NÉOVOLT GRID+ est un projet académique réalisé dans le cadre de la formation ESIC CPID.

L'objectif est de concevoir une plateforme de gestion, d'analyse et de sécurisation des données énergétiques issues de compteurs communicants afin d'améliorer la prise de décision, la prévision de consommation et la résilience des infrastructures.

---

## Structure du projet

### Volet A – Gouvernance et Pilotage

- Note de cadrage
- Business Case
- Gouvernance des données
- Gestion des risques
- Conduite du changement

### Volet B – Data Analyst

- Analyse qualitative et quantitative
- Data Storytelling
- Tableaux de bord Power BI
- Détection d'anomalies et de signaux de fraude

### Volet C – Data Science

- Prévision de consommation énergétique
- Machine Learning
- MLOps
- Application de démonstration Flask

### Volet D – Data Engineering

- Pipeline ETL
- PostgreSQL
- FastAPI
- Docker & Docker Compose

### Volet E – Cybersécurité et Conformité

- Analyse des risques cyber
- Prototype SOC
- DevSecOps
- PCA / PRA
- RGPD & NIS2

---

## Architecture globale

```text
Sources de données
        ↓
Pipeline ETL (Volet D)
        ↓
PostgreSQL
        ↓
API FastAPI
        ↓
Power BI (Volet B)
        ↓
Machine Learning (Volet C)

Logs API
        ↓
SOC & Dashboard Sécurité (Volet E)
