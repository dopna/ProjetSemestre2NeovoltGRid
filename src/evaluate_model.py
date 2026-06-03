import joblib
import pandas as pd
import matplotlib.pyplot as plt

from .config import BEST_MODEL_FILE, REPORTS_DIR, DATASET_MODEL_FILE
from .feature_engineering import get_feature_target


def main():
    df = pd.read_csv(DATASET_MODEL_FILE)

    artefact = joblib.load(BEST_MODEL_FILE)
    model = artefact["model"]
    model_name = artefact["model_name"]

    X, y, features = get_feature_target(df)

    split_index = int(len(df) * 0.8)

    X_test = X.iloc[split_index:]
    y_test = y.iloc[split_index:]

    predictions = model.predict(X_test)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = pd.DataFrame({
        "y_reel": y_test.values,
        "y_predit": predictions
    })

    results.to_csv(REPORTS_DIR / "predictions.csv", index=False)

    plt.figure(figsize=(12, 5))
    plt.plot(results["y_reel"].head(200).values, label="Consommation réelle")
    plt.plot(results["y_predit"].head(200).values, label="Consommation prédite")
    plt.title(f"Consommation réelle vs prédite - {model_name}")
    plt.xlabel("Observations")
    plt.ylabel("Consommation kWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "prediction_vs_reel.png")
    plt.show()

    print("Graphique sauvegardé dans reports/prediction_vs_reel.png")
    print("Prédictions sauvegardées dans reports/predictions.csv")


if __name__ == "__main__":
    main()