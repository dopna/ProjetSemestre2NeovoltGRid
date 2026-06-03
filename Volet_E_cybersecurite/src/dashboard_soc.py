import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ALERTES_FILE = BASE_DIR / "reports" / "alertes_securite.csv"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_alerts():
    df = pd.read_csv(ALERTES_FILE)

    if "horodatage" in df.columns:
        df["horodatage"] = pd.to_datetime(df["horodatage"], errors="coerce")

    return df


def plot_alerts_by_type(df):
    counts = df["type_alerte"].value_counts()

    plt.figure(figsize=(10, 5))
    counts.plot(kind="bar")
    plt.title("Répartition des alertes par type")
    plt.xlabel("Type d'alerte")
    plt.ylabel("Nombre d'alertes")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "alertes_par_type.png")
    plt.close()


def plot_alerts_by_criticite(df):
    counts = df["criticite"].value_counts()

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar")
    plt.title("Répartition des alertes par criticité")
    plt.xlabel("Criticité")
    plt.ylabel("Nombre d'alertes")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "alertes_par_criticite.png")
    plt.close()

def plot_top_users(df):
    counts = df["utilisateur"].dropna().value_counts().head(10)

    plt.figure(figsize=(10, 5))
    counts.plot(kind="bar")
    plt.title("Top 10 des utilisateurs associés aux alertes")
    plt.xlabel("Utilisateur")
    plt.ylabel("Nombre d'alertes")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "top_utilisateurs_alertes.png")
    plt.close()

def plot_top_ips(df):
    counts = df["source_ip"].dropna().value_counts().head(10)

    plt.figure(figsize=(10, 5))
    counts.plot(kind="bar")
    plt.title("Top 10 des adresses IP sources")
    plt.xlabel("Adresse IP")
    plt.ylabel("Nombre d'alertes")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "top_ip_alertes.png")
    plt.close()

def create_summary(df):
    summary = {
        "nombre_total_alertes": len(df),
        "alertes_par_type": df["type_alerte"].value_counts().to_dict(),
        "alertes_par_criticite": df["criticite"].value_counts().to_dict(),
        "top_utilisateurs": df["utilisateur"].dropna().value_counts().head(10).to_dict(),
        "top_ips": df["source_ip"].dropna().value_counts().head(10).to_dict(),
    }

    summary_file = REPORTS_DIR / "resume_soc.txt"

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("RÉSUMÉ SOC - NÉOVOLT GRID+\n")
        f.write("=" * 40 + "\n\n")

        f.write(f"Nombre total d'alertes : {summary['nombre_total_alertes']}\n\n")

        f.write("Alertes par type :\n")
        for key, value in summary["alertes_par_type"].items():
            f.write(f"- {key} : {value}\n")

        f.write("\nAlertes par criticité :\n")
        for key, value in summary["alertes_par_criticite"].items():
            f.write(f"- {key} : {value}\n")

        f.write("\nTop utilisateurs :\n")
        for key, value in summary["top_utilisateurs"].items():
            f.write(f"- {key} : {value}\n")

        f.write("\nTop IP sources :\n")
        for key, value in summary["top_ips"].items():
            f.write(f"- {key} : {value}\n")

    return summary

def main():
    df = load_alerts()

    if df.empty:
        print("Aucune alerte trouvée.")
        return

    plot_alerts_by_type(df)
    plot_alerts_by_criticite(df)
    plot_top_users(df)
    plot_top_ips(df)
    summary = create_summary(df)

    print("Dashboard SOC généré avec succès.")
    print(f"Nombre total d'alertes : {summary['nombre_total_alertes']}")
    print(f"Fichiers générés dans : {REPORTS_DIR}")

if __name__ == "__main__":
    main()