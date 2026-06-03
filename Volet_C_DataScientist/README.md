# Néovolt Grid+ — Volet C Data Scientist

## Objectif
Construire un modèle de prévision de consommation énergétique à partir des relevés de consommation, de la météo et des caractéristiques des compteurs/clients.

## Cas d'usage principal
Prévision de consommation journalière en kWh.

## Datasets utilisés
- `releves_consommation.csv` : historique de consommation
- `meteo.csv` : variables climatiques par zone
- `compteurs.csv` : caractéristiques techniques des points de livraison
- `clients.csv` : segmentation client

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Entraînement
Depuis la racine du projet :
```bash
python -m src.train_model
```

## Résultats générés
- `data/processed/dataset_modele_consommation.csv`
- `models/*.pkl`
- `reports/model_metrics.csv`
- `reports/features.json`

## Métriques suivies
- MAE
- RMSE
- R²

## MLOps proposé
- Versioning du code via GitHub
- Sauvegarde des modèles dans `models/`
- Suivi des expérimentations dans `reports/model_metrics.csv`
- Réentraînement mensuel recommandé
- Monitoring de dérive des données et de dégradation du RMSE
