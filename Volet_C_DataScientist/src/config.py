from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

CONSO_FILE = RAW_DATA_DIR / "releves_consommation.csv"
METEO_FILE = RAW_DATA_DIR / "meteo.csv"
COMPTEURS_FILE = RAW_DATA_DIR / "compteurs.csv"
CLIENTS_FILE = RAW_DATA_DIR / "clients.csv"
DATASET_MODEL_FILE = PROCESSED_DATA_DIR / "dataset_modele_consommation.csv"
BEST_MODEL_FILE = MODELS_DIR / "best_model.pkl"
