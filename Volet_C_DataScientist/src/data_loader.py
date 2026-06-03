import pandas as pd

from .config import (CONSO_FILE, METEO_FILE, COMPTEURS_FILE)

def load_data():

    consommation = pd.read_csv(CONSO_FILE)
    meteo = pd.read_csv(METEO_FILE)
    compteurs = pd.read_csv(COMPTEURS_FILE)

    consommation["date"] = pd.to_datetime(consommation["date"])
    meteo["date"] = pd.to_datetime(meteo["date"])

    return consommation, meteo, compteurs