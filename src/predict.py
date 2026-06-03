import joblib
import pandas as pd

from .config import BEST_MODEL_FILE

# Chargement du meilleur modèle sauvegardé
artefact = joblib.load(BEST_MODEL_FILE)
model = artefact["model"]
features = artefact["features"]
model_name = artefact["model_name"]

def predict_consumption(input_data):
    """
    Effectue une prédiction de consommation énergétique.
    Paramètres
    ----------
    input_data : dict ou pandas.DataFrame
    Exemple :
    {
        "temp_moyenne_c": 15,
        "temp_min_c": 10,
        "temp_max_c": 18,
        "jour": 15,
        "mois": 6,
        "jour_semaine": 2,
        "weekend": 0,
        "lag_1": 125,
        "lag_7": 118,
        "rolling_7": 121
    }
    Retour
    ------
    float
    """

    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise ValueError(
            "input_data doit être un dictionnaire ou un DataFrame"
        )

    for feature in features:
        if feature not in df.columns:
            df[feature] = 0

    df = df[features]

    prediction = model.predict(df)
    return float(prediction[0])


def get_model_info():
    """
    Retourne les informations du modèle chargé.
    """
    return {
        "model_name": model_name,
        "features": features
    }


if __name__ == "__main__":

    sample = {
        "temp_moyenne_c": 15,
        "temp_min_c": 10,
        "temp_max_c": 18,
        "jour": 15,
        "mois": 6,
        "jour_semaine": 2,
        "weekend": 0,
        "lag_1": 125,
        "lag_7": 118,
        "rolling_7": 121
    }
    prediction = predict_consumption(sample)
    print(f"Modèle utilisé : {model_name}")
    print(f"Consommation prédite : {prediction:.2f} kWh")