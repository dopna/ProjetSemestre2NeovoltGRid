import joblib
import pandas as pd
import matplotlib.pyplot as plt

from .config import BEST_MODEL_FILE, REPORTS_DIR


def main():

    artefact = joblib.load(BEST_MODEL_FILE)
    model = artefact["model"]
    model_name = artefact["model_name"]
    features = artefact["features"]
    if not hasattr(model, "feature_importances_"):
        print("Ce modèle ne fournit pas les importances.")
        return
    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    })
    importance = importance.sort_values(
        "importance",
        ascending=False
    )
    print(importance.head(20))
    importance.to_csv(
        REPORTS_DIR / "feature_importance.csv",
        index=False
    )
    plt.figure(figsize=(10, 6))
    plt.barh(
        importance["feature"].head(15),
        importance["importance"].head(15)
    )
    plt.gca().invert_yaxis()
    plt.title(
        f"Importance des variables - {model_name}"
    )
    plt.tight_layout()
    plt.savefig(
        REPORTS_DIR / "feature_importance.png"
    )
    plt.show()

if __name__ == "__main__":
    main()