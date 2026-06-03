from src.predict import predict_consumption, get_model_info

print(get_model_info())

sample = {
    "temp_moyenne_c": 15,
    "temp_min_c": 10,
    "temp_max_c": 18,
    "jour": 15,
    "mois": 6,
    "annee": 2025,
    "jour_semaine": 2,
    "weekend": 0,
    "puissance_souscrite_kva": 9,
    "lag_1": 120,
    "lag_7": 115,
    "rolling_7": 118
}

prediction = predict_consumption(sample)

print(f"Consommation prédite : {prediction:.2f} kWh")