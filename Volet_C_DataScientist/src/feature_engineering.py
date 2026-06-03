import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée les variables explicatives pour le modèle
    de prévision de consommation.
    """

    df = df.sort_values(["id_pdl", "date"]).copy()

    # Variables temporelles
    df["annee"] = df["date"].dt.year
    df["mois"] = df["date"].dt.month
    df["jour"] = df["date"].dt.day
    df["jour_semaine"] = df["date"].dt.dayofweek
    df["weekend"] = (df["jour_semaine"] >= 5).astype(int)

    # Variables de retard par compteur
    df["lag_1"] = (
        df.groupby("id_pdl")["consommation_kwh"]
        .shift(1)
    )

    df["lag_7"] = (
        df.groupby("id_pdl")["consommation_kwh"]
        .shift(7)
    )

    df["rolling_7"] = (
        df.groupby("id_pdl")["consommation_kwh"]
        .transform(lambda s: s.shift(1).rolling(7).mean())
    )

    # Encodage des variables catégorielles si elles existent
    categorical_cols = [
        "zone",
        "type_client",
        "type_chauffage",
        "type_compteur",
        "segment"
    ]

    existing_cols = [
        col for col in categorical_cols
        if col in df.columns
    ]

    df = pd.get_dummies(
        df,
        columns=existing_cols,
        drop_first=True
    )

    # Nettoyage final
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    return df


def get_feature_target(df: pd.DataFrame):
    """
    Sépare les variables explicatives X,
    la cible y et la liste des features.
    """

    target = "consommation_kwh"

    excluded_cols = {
        target,
        "id_pdl",
        "id_client",
        "date",
        "date_pose",
        "date_entree",
        "commune",
        "code_postal",
        "statut"
    }

    features = [
        col for col in df.columns
        if col not in excluded_cols
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    X = df[features]
    y = df[target]

    return X, y, features