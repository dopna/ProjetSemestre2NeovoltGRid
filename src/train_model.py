import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False

from .config import (
    DATASET_MODEL_FILE,
    BEST_MODEL_FILE,
    MODELS_DIR,
    REPORTS_DIR
)

from .data_loader import load_data
from .preprocessing import clean_and_merge
from .feature_engineering import add_features, get_feature_target


def evaluate_model(y_true, y_pred):
    """
    Calcule les métriques d'évaluation du modèle.
    """

    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred))
    }


def train_all_models():
    """
    Charge les données, prépare le dataset,
    entraîne plusieurs modèles et sauvegarde le meilleur.
    """

    consommation, meteo, compteurs = load_data()

    df = clean_and_merge(consommation, meteo, compteurs)
    df = add_features(df)

    DATASET_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATASET_MODEL_FILE, index=False)

    X, y, features = get_feature_target(df)

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    models = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=30,
            max_depth=12,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=1
        ),
    }

    if HAS_XGBOOST:
        models["xgboost"] = XGBRegressor(
            n_estimators=80,
            learning_rate=0.08,
            max_depth=4,
            random_state=42,
            n_jobs=-1
        )

    results = []

    best_name = None
    best_model = None
    best_rmse = float("inf")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    for name, model in models.items():
        print(f"Entraînement du modèle : {name}")

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        metrics = evaluate_model(y_test, predictions)
        metrics["model"] = name

        results.append(metrics)

        joblib.dump(model, MODELS_DIR / f"{name}.pkl")

        if metrics["RMSE"] < best_rmse:
            best_rmse = metrics["RMSE"]
            best_name = name
            best_model = model

    results_df = pd.DataFrame(results).sort_values("RMSE")

    results_df.to_csv(
        REPORTS_DIR / "model_metrics.csv",
        index=False
    )

    joblib.dump(
        {
            "model": best_model,
            "features": features,
            "model_name": best_name
        },
        BEST_MODEL_FILE
    )

    with open(REPORTS_DIR / "features.json", "w", encoding="utf-8") as f:
        json.dump(features, f, ensure_ascii=False, indent=2)

    print("\nRésultats des modèles :")
    print(results_df)

    print(f"\nMeilleur modèle : {best_name}")
    print(f"Modèle sauvegardé dans : {BEST_MODEL_FILE}")

    return results_df


if __name__ == "__main__":
    train_all_models()