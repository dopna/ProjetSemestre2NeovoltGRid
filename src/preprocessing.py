import pandas as pd


def clean_and_merge(
    consommation: pd.DataFrame,
    meteo: pd.DataFrame,
    compteurs: pd.DataFrame
) -> pd.DataFrame:
    """
    Nettoie et fusionne les données nécessaires
    à la prévision de consommation.
    """

    consommation = consommation.drop_duplicates().copy()
    meteo = meteo.drop_duplicates().copy()
    compteurs = compteurs.drop_duplicates().copy()

    consommation["date"] = pd.to_datetime(consommation["date"])
    meteo["date"] = pd.to_datetime(meteo["date"])

    consommation = consommation.sort_values(["id_pdl", "date"])

    consommation["consommation_kwh"] = (
        consommation.groupby("id_pdl")["consommation_kwh"]
        .transform(lambda s: s.interpolate(limit_direction="both"))
    )

    df = consommation.merge(
        meteo,
        on=["date", "zone"],
        how="left"
    )

    df = df.merge(
        compteurs,
        on=["id_pdl", "zone"],
        how="left"
    )

    df = df.dropna(subset=["consommation_kwh"])

    return df