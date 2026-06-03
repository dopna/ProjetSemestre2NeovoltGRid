from src.data_loader import load_data

cons, meteo, compteurs = load_data()

print("=== CONSOMMATION ===")
print(cons.columns.tolist())

print("\n=== METEO ===")
print(meteo.columns.tolist())

print("\n=== COMPTEURS ===")
print(compteurs.columns.tolist())