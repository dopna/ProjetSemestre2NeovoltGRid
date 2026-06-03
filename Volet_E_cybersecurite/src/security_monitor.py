import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

LOGS_FILE = BASE_DIR / "data" / "journaux_securite.csv"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_logs():
    df = pd.read_csv(LOGS_FILE)
    df["horodatage"] = pd.to_datetime(df["horodatage"])
    return df


def detect_bruteforce(df):
    failed = df[
        (df["type_evenement"] == "connexion_echouee")
        | (df["resultat"] == "echec")
    ]

    alerts = (
        failed
        .groupby(["utilisateur", "source_ip"])
        .size()
        .reset_index(name="nb_echecs")
    )

    alerts = alerts[alerts["nb_echecs"] >= 5]

    alerts["type_alerte"] = "BRUTE_FORCE"
    alerts["criticite"] = "Haute"

    return alerts


def detect_access_denied(df):
    denied = df[df["type_evenement"] == "acces_refuse"]

    alerts = (
        denied
        .groupby(["utilisateur", "source_ip", "systeme"])
        .size()
        .reset_index(name="nb_acces_refuses")
    )

    alerts = alerts[alerts["nb_acces_refuses"] >= 3]

    alerts["type_alerte"] = "ACCES_REFUSES_REPETES"
    alerts["criticite"] = "Moyenne"

    return alerts


def detect_data_exports(df):
    exports = df[
        (df["type_evenement"] == "export_donnees")
        & (df["resultat"] == "succes")
    ].copy()

    exports["type_alerte"] = "EXPORT_DONNEES"
    exports["criticite"] = "Haute"

    return exports[
        [
            "horodatage",
            "utilisateur",
            "source_ip",
            "systeme",
            "type_evenement",
            "resultat",
            "type_alerte",
            "criticite"
        ]
    ]


def detect_sensitive_config_changes(df):
    changes = df[
        (df["type_evenement"] == "modification_config")
        & (df["resultat"] == "succes")
    ].copy()

    changes["type_alerte"] = "MODIFICATION_CONFIG"
    changes["criticite"] = "Critique"

    return changes[
        [
            "horodatage",
            "utilisateur",
            "source_ip",
            "systeme",
            "type_evenement",
            "resultat",
            "type_alerte",
            "criticite"
        ]
    ]


def detect_scada_activity(df):
    scada = df[df["systeme"] == "scada"].copy()

    scada["type_alerte"] = "ACTIVITE_SCADA"
    scada["criticite"] = "Critique"

    return scada[
        [
            "horodatage",
            "utilisateur",
            "source_ip",
            "systeme",
            "type_evenement",
            "resultat",
            "type_alerte",
            "criticite"
        ]
    ]

def detect_external_provider_activity(df):
    provider = df[df["utilisateur"] == "prestataire_ext"].copy()

    provider["type_alerte"] = "ACTIVITE_PRESTATAIRE"
    provider["criticite"] = "Haute"

    return provider[
        [
            "horodatage",
            "utilisateur",
            "source_ip",
            "systeme",
            "type_evenement",
            "resultat",
            "type_alerte",
            "criticite"
        ]
    ]


def normalize_alerts(alerts):
    normalized = []

    for alert in alerts:
        temp = alert.copy()

        for col in [
            "horodatage",
            "utilisateur",
            "source_ip",
            "systeme",
            "type_evenement",
            "resultat",
            "type_alerte",
            "criticite"
        ]:
            if col not in temp.columns:
                temp[col] = None

        normalized.append(
            temp[
                [
                    "horodatage",
                    "utilisateur",
                    "source_ip",
                    "systeme",
                    "type_evenement",
                    "resultat",
                    "type_alerte",
                    "criticite"
                ]
            ]
        )
    return pd.concat(normalized, ignore_index=True)

def main():
    df = load_logs()

    alerts = [
        detect_bruteforce(df),
        detect_access_denied(df),
        detect_data_exports(df),
        detect_sensitive_config_changes(df),
        detect_scada_activity(df),
        detect_external_provider_activity(df)
    ]

    all_alerts = normalize_alerts(alerts)

    output_file = REPORTS_DIR / "alertes_securite.csv"
    all_alerts.to_csv(output_file, index=False)

    print("Analyse terminée.")
    print(f"Nombre total d'événements analysés : {len(df)}")
    print(f"Nombre total d'alertes générées : {len(all_alerts)}")
    print(f"Rapport généré : {output_file}")

    print("\nRépartition des alertes :")
    print(all_alerts["type_alerte"].value_counts())


if __name__ == "__main__":
    main()