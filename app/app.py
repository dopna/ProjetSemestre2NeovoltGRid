from flask import Flask, render_template, request
import pandas as pd
import joblib
from pathlib import Path

app = Flask(__name__)
ARTEFACT_PATH = Path(__file__).resolve().parents[1] / "models" / "best_model.pkl"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    artefact = joblib.load(ARTEFACT_PATH)
    features = artefact["features"]
    model = artefact["model"]

    values = {feature: float(request.form.get(feature, 0)) for feature in features}
    X = pd.DataFrame([values])
    prediction = model.predict(X)[0]
    return render_template("index.html", prediction_text=f"Consommation prédite : {prediction:.2f} kWh")

if __name__ == "__main__":
    app.run(debug=True)
