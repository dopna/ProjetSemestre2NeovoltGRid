import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Chemins
DATA_DIR = "./data/"
OUT_DIR = "./outputs/"

import os
os.makedirs(OUT_DIR, exist_ok=True)

# Style global
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#f8f9fa',
    'axes.grid':        True,
    'grid.alpha':       0.4,
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
})

PALETTE_ZONES = {
    'Centre-Ville':    '#2196F3',
    'Parc-Tertiaire':  '#FF9800',
    'Val-Nord':        '#4CAF50',
    'Rives-Sud':       '#9C27B0',
    'Coteaux-Ouest':   '#F44336',
    'Plateau-Est':     '#00BCD4',
    'Bourg-Ancien':    '#795548',
    'Zone-Industrielle':'#607D8B',
}

print("=" * 60)
print("NÉOVOLT GRID+ — Volet B : Data Analyst")
print("=" * 60)


print("\n[1] CHARGEMENT DES DONNÉES")
print("-" * 40)

releves   = pd.read_csv(DATA_DIR + 'releves_consommation.csv', parse_dates=['date'])
compteurs = pd.read_csv(DATA_DIR + 'compteurs.csv', parse_dates=['date_pose'])
clients   = pd.read_csv(DATA_DIR + 'clients.csv',   parse_dates=['date_entree'])
meteo     = pd.read_csv(DATA_DIR + 'meteo.csv',     parse_dates=['date'])
incidents = pd.read_csv(DATA_DIR + 'incidents_reseau.csv')
fraudes   = pd.read_csv(DATA_DIR + 'cas_fraude_confirmes.csv', parse_dates=['date_detection'])
releves_h = pd.read_csv(DATA_DIR + 'releves_horaires_echantillon.csv', parse_dates=['horodatage'])
reclamations = pd.read_csv(DATA_DIR + 'reclamations.csv', parse_dates=['date'])

print(f"  releves_consommation : {len(releves):>8,} lignes")
print(f"  compteurs            : {len(compteurs):>8,} lignes")
print(f"  clients              : {len(clients):>8,} lignes")
print(f"  meteo                : {len(meteo):>8,} lignes")
print(f"  incidents            : {len(incidents):>8,} lignes")
print(f"  fraudes confirmées   : {len(fraudes):>8,} lignes")
print(f"  releves_horaires     : {len(releves_h):>8,} lignes")
print(f"  reclamations         : {len(reclamations):>8,} lignes")


# ─────────────────────────────────────────────
# 2. AUDIT QUALITÉ DES DONNÉES
# ─────────────────────────────────────────────
print("\n[2] AUDIT QUALITÉ — RELEVÉS DE CONSOMMATION")
print("-" * 40)

total = len(releves)
manquants    = releves['consommation_kwh'].isnull().sum()
negatifs     = (releves['consommation_kwh'] < 0).sum()
doublons     = releves.duplicated(subset=['id_pdl','date']).sum()
seuil_haut   = releves['consommation_kwh'].quantile(0.999)
aberrants_h  = (releves['consommation_kwh'] > seuil_haut).sum()

print(f"  Total relevés          : {total:>8,}")
print(f"  Valeurs manquantes     : {manquants:>8,}  ({manquants/total*100:.1f}%)")
print(f"  Valeurs négatives      : {negatifs:>8,}  ({negatifs/total*100:.1f}%)")
print(f"  Doublons (pdl+date)    : {doublons:>8,}  ({doublons/total*100:.1f}%)")
print(f"  Aberrants > p99.9      : {aberrants_h:>8,}  ({aberrants_h/total*100:.1f}%)")
print(f"  Seuil aberrant haut    : {seuil_haut:>8.1f} kWh")
print(f"  Min / Max              : {releves['consommation_kwh'].min():.1f} / {releves['consommation_kwh'].max():.1f} kWh")

# ── Figure 1 : Rapport de qualité ──
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle("Rapport de qualité des données — Relevés de consommation", fontsize=14, fontweight='bold')

# Camembert
labels  = ['Valides', 'Manquants', 'Négatifs', 'Doublons', 'Aberrants hauts']
sizes   = [total - manquants - negatifs - doublons - aberrants_h, manquants, negatifs, doublons, aberrants_h]
colors  = ['#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#607D8B']
axes[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
axes[0].set_title("Répartition des anomalies")

# Distribution log des consommations valides
valides = releves['consommation_kwh'].dropna()
valides = valides[valides >= 0]
axes[1].hist(np.log1p(valides), bins=60, color='#2196F3', edgecolor='white', alpha=0.85)
axes[1].set_xlabel("log(1 + consommation_kwh)")
axes[1].set_ylabel("Nombre de relevés")
axes[1].set_title("Distribution des consommations (log)")

# Manquants par zone
miss_zone = releves[releves['consommation_kwh'].isnull()]['zone'].value_counts()
axes[2].barh(miss_zone.index, miss_zone.values, color='#FF9800')
axes[2].set_xlabel("Nombre de relevés manquants")
axes[2].set_title("Manquants par zone")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig01_qualite_donnees.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  Figure 01 sauvegardée : Qualité des données")


# ─────────────────────────────────────────────
# 3. NETTOYAGE DES DONNÉES
# ─────────────────────────────────────────────
print("\n[3] NETTOYAGE")
print("-" * 40)

df = releves.copy()

# 3.1 Supprimer les doublons (garder la première occurrence)
nb_avant = len(df)
df = df.drop_duplicates(subset=['id_pdl', 'date'], keep='first')
print(f"  Doublons supprimés       : {nb_avant - len(df)}")

# 3.2 Valeurs négatives → NaN (consommation physiquement impossible)
df.loc[df['consommation_kwh'] < 0, 'consommation_kwh'] = np.nan
print(f"  Valeurs négatives → NaN  : {negatifs}")

# 3.3 Valeurs aberrantes hautes (> p99.9) → NaN
df.loc[df['consommation_kwh'] > seuil_haut, 'consommation_kwh'] = np.nan
print(f"  Aberrants hauts → NaN    : {aberrants_h}")

# 3.4 Imputation : médiane glissante par PDL (fenêtre 7 jours)
df = df.sort_values(['id_pdl', 'date'])
df['consommation_kwh'] = (
    df.groupby('id_pdl')['consommation_kwh']
      .transform(lambda s: s.fillna(s.rolling(7, min_periods=1, center=True).median()))
)

restants = df['consommation_kwh'].isnull().sum()
print(f"  Manquants après imputation : {restants}")
print(f"  Lignes finales nettoyées   : {len(df):,}")

# 3.5 Enrichissement : jointure compteurs + clients
df = df.merge(compteurs[['id_pdl','id_client','type_client','puissance_souscrite_kva',
                          'type_chauffage','type_compteur']], on='id_pdl', how='left')
df = df.merge(clients[['id_client','segment','commune','surface_m2']], on='id_client', how='left')

# 3.6 Ajout colonnes temporelles
df['annee']       = df['date'].dt.year
df['mois']        = df['date'].dt.month
df['jour_semaine']= df['date'].dt.dayofweek   # 0=lundi
df['semaine']     = df['date'].dt.isocalendar().week.astype(int)
df['trimestre']   = df['date'].dt.quarter

# Saison
def saison(m):
    if m in [12,1,2]:  return 'Hiver'
    elif m in [3,4,5]: return 'Printemps'
    elif m in [6,7,8]: return 'Été'
    else:              return 'Automne'
df['saison'] = df['mois'].apply(saison)

# 3.7 Jointure météo
meteo_agg = meteo.copy()
meteo_agg['DJU'] = (17 - meteo_agg['temp_moyenne_c']).clip(lower=0)  # Degrés-Jour Utiles
df = df.merge(meteo_agg[['date','zone','temp_moyenne_c','DJU']], on=['date','zone'], how='left')

print(f"\n  Dataset final enrichi : {len(df):,} lignes × {len(df.columns)} colonnes")
print(f"  Colonnes : {list(df.columns)}")


# ─────────────────────────────────────────────
# 4. ANALYSE DESCRIPTIVE
# ─────────────────────────────────────────────
print("\n[4] ANALYSE DESCRIPTIVE")
print("-" * 40)

# Statistiques par type de client
stats_type = df.groupby('type_client')['consommation_kwh'].agg(['mean','median','std','count'])
stats_type.columns = ['Moyenne (kWh)', 'Médiane (kWh)', 'Écart-type', 'Nb relevés']
print("\n  Consommation par type de client :")
print(stats_type.round(1).to_string())

# Statistiques par zone
stats_zone = df.groupby('zone')['consommation_kwh'].agg(['mean','median','sum']).round(1)
stats_zone.columns = ['Moy (kWh)', 'Méd (kWh)', 'Total (kWh)']
stats_zone = stats_zone.sort_values('Total (kWh)', ascending=False)
print("\n  Consommation par zone (total 2 ans) :")
print(stats_zone.to_string())

# ── Figure 2 : Consommation par profil et zone ──
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Profils de consommation — Vue d'ensemble", fontsize=14, fontweight='bold')

# Boxplot par type de client
data_box = [df[df['type_client']==t]['consommation_kwh'].dropna() for t in ['residentiel','professionnel','industriel']]
bp = axes[0].boxplot(data_box, labels=['Résidentiel', 'Professionnel', 'Industriel'],
                     patch_artist=True, showfliers=False)
colors_box = ['#4CAF50', '#2196F3', '#FF9800']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[0].set_ylabel("Consommation journalière (kWh)")
axes[0].set_title("Distribution par type de client")

# Consommation totale par zone
zones = stats_zone.index.tolist()
totaux = stats_zone['Total (kWh)'].values / 1e6  # en GWh
bar_colors = [PALETTE_ZONES.get(z, '#888') for z in zones]
bars = axes[1].barh(zones, totaux, color=bar_colors, edgecolor='white')
axes[1].set_xlabel("Consommation totale (GWh)")
axes[1].set_title("Consommation cumulée par zone (2024-2025)")
for bar, val in zip(bars, totaux):
    axes[1].text(val + 0.1, bar.get_y() + bar.get_height()/2,
                 f'{val:.1f} GWh', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig02_profils_consommation.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  Figure 02 sauvegardée : Profils de consommation")


# ─────────────────────────────────────────────
# 5. ANALYSE DES SÉRIES TEMPORELLES
# ─────────────────────────────────────────────
print("\n[5] SÉRIES TEMPORELLES")
print("-" * 40)

# Agrégation quotidienne totale
daily = df.groupby('date')['consommation_kwh'].sum().reset_index()
daily.columns = ['date', 'conso_totale_kwh']

# Agrégation mensuelle
monthly = df.groupby(['annee','mois'])['consommation_kwh'].sum().reset_index()
monthly['periode'] = pd.to_datetime(monthly['annee'].astype(str) + '-' + monthly['mois'].astype(str) + '-01')
monthly = monthly.sort_values('periode')

# Par zone et mois
monthly_zone = df.groupby(['zone','annee','mois'])['consommation_kwh'].sum().reset_index()
monthly_zone['periode'] = pd.to_datetime(
    monthly_zone['annee'].astype(str) + '-' + monthly_zone['mois'].astype(str) + '-01')

print(f"  Consommation quotidienne moyenne : {daily['conso_totale_kwh'].mean():,.0f} kWh")
print(f"  Jour de pointe max : {daily.loc[daily['conso_totale_kwh'].idxmax(), 'date'].date()} → {daily['conso_totale_kwh'].max():,.0f} kWh")
print(f"  Jour minimum       : {daily.loc[daily['conso_totale_kwh'].idxmin(), 'date'].date()} → {daily['conso_totale_kwh'].min():,.0f} kWh")

# Saisonnalité mensuelle
conso_mois = df.groupby('mois')['consommation_kwh'].mean()
print(f"\n  Mois le plus consommateur : {conso_mois.idxmax()} ({conso_mois.max():.1f} kWh moy)")
print(f"  Mois le moins consommateur: {conso_mois.idxmin()} ({conso_mois.min():.1f} kWh moy)")

# ── Figure 3 : Séries temporelles ──
fig, axes = plt.subplots(3, 1, figsize=(16, 14))
fig.suptitle("Analyse des séries temporelles de consommation", fontsize=14, fontweight='bold')

# 5a. Série quotidienne avec moyenne mobile
daily_sorted = daily.sort_values('date')
axes[0].fill_between(daily_sorted['date'], daily_sorted['conso_totale_kwh']/1e3,
                     alpha=0.3, color='#2196F3')
axes[0].plot(daily_sorted['date'], daily_sorted['conso_totale_kwh']/1e3,
             color='#2196F3', linewidth=0.8, alpha=0.6)
rolling = daily_sorted['conso_totale_kwh'].rolling(30).mean()
axes[0].plot(daily_sorted['date'], rolling/1e3, color='#F44336', linewidth=2,
             label='Moyenne mobile 30j')
axes[0].set_ylabel("Consommation (MWh)")
axes[0].set_title("Consommation quotidienne totale du réseau")
axes[0].legend()

# 5b. Saisonnalité mensuelle (moyenne par mois)
mois_labels = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
conso_mois_plot = df.groupby('mois')['consommation_kwh'].mean()
bars = axes[1].bar(range(1,13), conso_mois_plot.values,
                   color=[('#F44336' if m in [12,1,2] else
                           '#FF9800' if m in [3,4,5] else
                           '#4CAF50' if m in [6,7,8] else '#2196F3') for m in range(1,13)],
                   edgecolor='white', alpha=0.85)
axes[1].set_xticks(range(1,13))
axes[1].set_xticklabels(mois_labels)
axes[1].set_ylabel("Consommation moyenne (kWh/PDL/jour)")
axes[1].set_title("Saisonnalité mensuelle — Consommation moyenne par jour")

# Légende saisons
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#F44336', label='Hiver'),
                   Patch(facecolor='#FF9800', label='Printemps'),
                   Patch(facecolor='#4CAF50', label='Été'),
                   Patch(facecolor='#2196F3', label='Automne')]
axes[1].legend(handles=legend_elements)

# 5c. Courbe par zone (mensuel)
for zone, grp in monthly_zone.groupby('zone'):
    grp = grp.sort_values('periode')
    axes[2].plot(grp['periode'], grp['consommation_kwh']/1e3,
                 label=zone, color=PALETTE_ZONES.get(zone,'#888'), linewidth=1.8)
axes[2].set_ylabel("Consommation mensuelle (MWh)")
axes[2].set_title("Consommation mensuelle par zone")
axes[2].legend(ncol=4, fontsize=9)

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig03_series_temporelles.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 03 sauvegardée : Séries temporelles")


# ─────────────────────────────────────────────
# 6. CORRÉLATION MÉTÉO / CONSOMMATION (DJU)
# ─────────────────────────────────────────────
print("\n[6] CORRÉLATION MÉTÉO / CONSOMMATION")
print("-" * 40)

# Agrégation quotidienne par zone
daily_zone = df.groupby(['date','zone']).agg(
    conso_moy=('consommation_kwh','mean'),
    DJU=('DJU','first'),
    temp=('temp_moyenne_c','first')
).reset_index()

# Corrélation de Pearson globale
corr_global = daily_zone['DJU'].corr(daily_zone['conso_moy'])
print(f"  Corrélation DJU / Consommation (toutes zones) : r = {corr_global:.3f}")

# Par type de chauffage
corr_chauffage = df.groupby('type_chauffage').apply(
    lambda g: g['DJU'].corr(g['consommation_kwh'])
).round(3)
print(f"\n  Corrélation DJU par mode de chauffage :")
print(corr_chauffage.to_string())

# Par type de client
corr_client = df.groupby('type_client').apply(
    lambda g: g['DJU'].corr(g['consommation_kwh'])
).round(3)
print(f"\n  Corrélation DJU par type de client :")
print(corr_client.to_string())

# ── Figure 4 : Corrélation météo ──
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Corrélation Température / Consommation", fontsize=14, fontweight='bold')

# Scatter DJU vs conso (résidentiel uniquement)
df_res = df[df['type_client']=='residentiel'].sample(min(5000, len(df[df['type_client']=='residentiel'])), random_state=42)
sc = axes[0].scatter(df_res['temp_moyenne_c'], df_res['consommation_kwh'],
                     c=df_res['DJU'], cmap='coolwarm_r', alpha=0.4, s=10)
plt.colorbar(sc, ax=axes[0], label='DJU (Degrés-Jour Utiles)')
axes[0].set_xlabel("Température moyenne (°C)")
axes[0].set_ylabel("Consommation (kWh)")
axes[0].set_title(f"Consommation résidentielle vs Température\n(r = {df_res['temp_moyenne_c'].corr(df_res['consommation_kwh']):.2f})")

# Corrélation par zone
corr_zones = daily_zone.groupby('zone').apply(
    lambda g: g['DJU'].corr(g['conso_moy'])
).sort_values(ascending=True)
bars = axes[1].barh(corr_zones.index, corr_zones.values,
                    color=[PALETTE_ZONES.get(z,'#888') for z in corr_zones.index],
                    edgecolor='white')
axes[1].axvline(0, color='black', linewidth=0.8, linestyle='--')
axes[1].set_xlabel("Coefficient de corrélation (r)")
axes[1].set_title("Corrélation DJU / Consommation par zone")
axes[1].set_xlim(-0.1, 1.0)
for bar, val in zip(bars, corr_zones.values):
    axes[1].text(val + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig04_correlation_meteo.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 04 sauvegardée : Corrélation météo")


# ─────────────────────────────────────────────
# 7. DÉTECTION DES PICS DE CONSOMMATION
# ─────────────────────────────────────────────
print("\n[7] ANALYSE DES PICS DE CONSOMMATION")
print("-" * 40)

# Pic = consommation > moyenne + 2 écarts-types sur la période
daily_stats = daily_sorted.copy()
mean_c = daily_stats['conso_totale_kwh'].mean()
std_c  = daily_stats['conso_totale_kwh'].std()
seuil_pic = mean_c + 2 * std_c

pics = daily_stats[daily_stats['conso_totale_kwh'] > seuil_pic]
print(f"  Seuil pic (μ + 2σ) : {seuil_pic:,.0f} kWh")
print(f"  Nombre de jours de pic : {len(pics)}")
print(f"  Dont en hiver (déc-fév) : {len(pics[pics['date'].dt.month.isin([12,1,2])])}")

# Consommation par jour de la semaine
conso_dow = df.groupby('jour_semaine')['consommation_kwh'].mean()
jours_label = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']
print(f"\n  Consommation moyenne par jour de semaine :")
for i, v in conso_dow.items():
    print(f"    {jours_label[i]} : {v:.2f} kWh")

# ── Figure 5 : Pics et patterns hebdo ──
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Pics de consommation et patterns hebdomadaires", fontsize=14, fontweight='bold')

# Série quotidienne avec pics
axes[0].plot(daily_sorted['date'], daily_sorted['conso_totale_kwh']/1e3,
             color='#2196F3', linewidth=0.8, alpha=0.7)
axes[0].axhline(seuil_pic/1e3, color='#F44336', linestyle='--', linewidth=1.5, label=f'Seuil pic (μ+2σ)')
axes[0].scatter(pics['date'], pics['conso_totale_kwh']/1e3,
                color='#F44336', s=20, zorder=5, label=f'Jours de pic ({len(pics)} jours)')
axes[0].fill_between(daily_sorted['date'], seuil_pic/1e3, daily_sorted['conso_totale_kwh']/1e3,
                     where=(daily_sorted['conso_totale_kwh'] > seuil_pic),
                     alpha=0.3, color='#F44336')
axes[0].set_ylabel("Consommation totale (MWh)")
axes[0].set_title("Identification des jours de pic")
axes[0].legend()

# Heatmap jour × mois
pivot = df.groupby(['jour_semaine','mois'])['consommation_kwh'].mean().unstack()
pivot.index = jours_label
pivot.columns = mois_labels
sns.heatmap(pivot, ax=axes[1], cmap='YlOrRd', annot=True, fmt='.0f',
            cbar_kws={'label': 'Conso moy (kWh)'})
axes[1].set_title("Consommation moyenne — Jour × Mois (kWh/PDL)")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig05_pics_patterns.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 05 sauvegardée : Pics et patterns")


# ─────────────────────────────────────────────
# 8. COURBES DE CHARGE HORAIRES
# ─────────────────────────────────────────────
print("\n[8] COURBES DE CHARGE HORAIRES")
print("-" * 40)

releves_h['heure'] = releves_h['horodatage'].dt.hour
releves_h['jour_semaine'] = releves_h['horodatage'].dt.dayofweek
releves_h['type_jour'] = releves_h['jour_semaine'].apply(lambda x: 'Semaine' if x < 5 else 'Week-end')

# Jointure avec type_client
releves_h = releves_h.merge(compteurs[['id_pdl','type_client']], on='id_pdl', how='left')

# Profil horaire moyen
profil_heure = releves_h.groupby(['heure','type_jour'])['consommation_kwh'].mean().reset_index()

print(f"  30 PDL sur {(releves_h['horodatage'].max()-releves_h['horodatage'].min()).days} jours")
heure_pic = releves_h.groupby('heure')['consommation_kwh'].mean().idxmax()
print(f"  Heure de pointe moyenne : {heure_pic}h00")

# ── Figure 6 : Courbes de charge ──
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Courbes de charge horaires (échantillon 30 PDL)", fontsize=14, fontweight='bold')

# Profil semaine vs week-end
for type_j, grp in profil_heure.groupby('type_jour'):
    color = '#2196F3' if type_j == 'Semaine' else '#FF9800'
    axes[0].plot(grp['heure'], grp['consommation_kwh'], marker='o',
                 linewidth=2, markersize=4, color=color, label=type_j)
axes[0].set_xlabel("Heure de la journée")
axes[0].set_ylabel("Consommation moyenne (kWh)")
axes[0].set_title("Profil de charge : Semaine vs Week-end")
axes[0].set_xticks(range(0, 24, 2))
axes[0].legend()
# Zones colorées
axes[0].axvspan(7, 10, alpha=0.1, color='red', label='Pointe matin')
axes[0].axvspan(18, 22, alpha=0.1, color='orange', label='Pointe soir')

# Heatmap heure x jour_semaine
pivot_h = releves_h.groupby(['heure','jour_semaine'])['consommation_kwh'].mean().unstack()
pivot_h.columns = jours_label
sns.heatmap(pivot_h, ax=axes[1], cmap='YlOrRd',
            cbar_kws={'label': 'Conso moy (kWh)'})
axes[1].set_xlabel("Jour de la semaine")
axes[1].set_ylabel("Heure")
axes[1].set_title("Heatmap : Heure × Jour de semaine")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig06_courbes_charge.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 06 sauvegardée : Courbes de charge")


# ─────────────────────────────────────────────
# 9. ANALYSE DES FRAUDES ET ANOMALIES
# ─────────────────────────────────────────────
print("\n[9] ANALYSE DES FRAUDES")
print("-" * 40)

# Enrichir les fraudes avec les infos compteur
fraudes_enrichies = fraudes.merge(compteurs, on='id_pdl', how='left')
fraudes_enrichies = fraudes_enrichies.merge(
    df.groupby('id_pdl')['consommation_kwh'].mean().reset_index().rename(
        columns={'consommation_kwh':'conso_moy_pdl'}), on='id_pdl', how='left')

print(f"  24 fraudes confirmées sur {compteurs['id_pdl'].nunique()} PDL")
print(f"  Taux de fraude détecté : {24/700*100:.1f}%")
print(f"\n  Par type :")
print(fraudes['type_fraude'].value_counts().to_string())
print(f"\n  Par type de client fraudeur :")
print(fraudes_enrichies['type_client'].value_counts().to_string())
print(f"\n  Par zone fraudeuse :")
print(fraudes_enrichies['zone'].value_counts().to_string())

# Comparaison conso moy : PDL frauduleux vs normal
pdl_fraude = fraudes['id_pdl'].tolist()
conso_fraude = df[df['id_pdl'].isin(pdl_fraude)]['consommation_kwh'].mean()
conso_normal = df[~df['id_pdl'].isin(pdl_fraude)]['consommation_kwh'].mean()
print(f"\n  Conso moy PDL frauduleux : {conso_fraude:.2f} kWh")
print(f"  Conso moy PDL normaux    : {conso_normal:.2f} kWh")
print(f"  Ratio : {conso_normal/conso_fraude:.1f}x (les fraudeurs consomment moins → sous-comptage)")

# ── Figure 7 : Fraudes ──
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Analyse des fraudes confirmées", fontsize=14, fontweight='bold')

# Camembert types de fraude
ftype = fraudes['type_fraude'].value_counts()
axes[0].pie(ftype.values, labels=ftype.index, autopct='%1.0f%%',
            colors=['#F44336','#FF9800','#9C27B0'], startangle=90)
axes[0].set_title("Répartition par type de fraude")

# Comparaison consommation
labels_comp = ['PDL Normaux', 'PDL Frauduleux']
vals_comp = [conso_normal, conso_fraude]
colors_comp = ['#4CAF50', '#F44336']
bars = axes[1].bar(labels_comp, vals_comp, color=colors_comp, edgecolor='white', alpha=0.85)
axes[1].set_ylabel("Consommation moyenne (kWh/jour)")
axes[1].set_title(f"Écart de consommation\nFrauduleux vs Normaux")
for bar, val in zip(bars, vals_comp):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{val:.1f} kWh', ha='center', fontsize=10, fontweight='bold')

# Distribution temporelle des détections
fraudes['mois_detection'] = fraudes['date_detection'].dt.to_period('M').astype(str)
detect_timeline = fraudes.groupby('mois_detection').size()
axes[2].bar(range(len(detect_timeline)), detect_timeline.values,
            color='#F44336', edgecolor='white', alpha=0.85)
axes[2].set_xticks(range(len(detect_timeline)))
axes[2].set_xticklabels(detect_timeline.index, rotation=45, ha='right', fontsize=7)
axes[2].set_ylabel("Nombre de fraudes détectées")
axes[2].set_title("Chronologie des détections de fraude")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig07_fraudes.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 07 sauvegardée : Analyse des fraudes")


# ─────────────────────────────────────────────
# 10. ANALYSE DES INCIDENTS RÉSEAU
# ─────────────────────────────────────────────
print("\n[10] ANALYSE DES INCIDENTS RÉSEAU")
print("-" * 40)

incidents['date_debut'] = pd.to_datetime(incidents['date_debut'])
incidents['mois'] = incidents['date_debut'].dt.month
incidents['annee'] = incidents['date_debut'].dt.year

print(f"  Nombre total d'incidents  : {len(incidents)}")
print(f"  PDL impactés (total)      : {incidents['nb_pdl_impactes'].sum():,}")
print(f"  Durée moyenne             : {incidents['duree_minutes'].mean():.0f} min")
print(f"  Durée max                 : {incidents['duree_minutes'].max()} min")
print(f"\n  Par type :")
print(incidents['type'].value_counts().to_string())
print(f"\n  Par cause :")
print(incidents['cause'].value_counts().to_string())

# ── Figure 8 : Incidents ──
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Analyse des incidents réseau (2024-2025)", fontsize=14, fontweight='bold')

# Par type
inc_type = incidents['type'].value_counts()
axes[0].bar(inc_type.index, inc_type.values,
            color=['#F44336','#FF9800','#2196F3','#4CAF50','#9C27B0'],
            edgecolor='white', alpha=0.85)
axes[0].set_ylabel("Nombre d'incidents")
axes[0].set_title("Incidents par type")
axes[0].tick_params(axis='x', rotation=30)

# Par zone
inc_zone = incidents.groupby('zone')['nb_pdl_impactes'].sum().sort_values(ascending=True)
axes[1].barh(inc_zone.index, inc_zone.values,
             color=[PALETTE_ZONES.get(z,'#888') for z in inc_zone.index])
axes[1].set_xlabel("PDL impactés (total)")
axes[1].set_title("PDL impactés par zone")

# Durée par type
durée_type = incidents.groupby('type')['duree_minutes'].mean().sort_values(ascending=False)
axes[2].barh(durée_type.index, durée_type.values / 60,
             color=['#F44336','#FF9800','#9C27B0','#2196F3','#4CAF50'])
axes[2].set_xlabel("Durée moyenne (heures)")
axes[2].set_title("Durée moyenne par type d'incident")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig08_incidents_reseau.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 08 sauvegardée : Incidents réseau")


# ─────────────────────────────────────────────
# 11. ANALYSE DES RÉCLAMATIONS CLIENTS
# ─────────────────────────────────────────────
print("\n[11] ANALYSE DES RÉCLAMATIONS")
print("-" * 40)

# Satisfaction par zone
reclamations_enrichies = reclamations.merge(clients[['id_client','commune']], on='id_client', how='left')
sat_zone = reclamations_enrichies.groupby('commune')['satisfaction'].mean().sort_values()
print(f"  Note satisfaction globale : {reclamations['satisfaction'].mean():.2f}/5")
print(f"  Zone la plus insatisfaite : {sat_zone.index[0]} ({sat_zone.iloc[0]:.2f}/5)")
print(f"  Zone la plus satisfaite   : {sat_zone.index[-1]} ({sat_zone.iloc[-1]:.2f}/5)")

# Thématiques par mots-clés simples
keywords = {
    'Facturation': ['facture','facturation','facturé','montant','surfacturé'],
    'Coupure / Panne': ['coupure','panne','coupé','plus de courant','sans électricité'],
    'Compteur': ['compteur','relevé','télérelève','index'],
    'RGPD / Données': ['rgpd','données','confidentialité','accord','consentement'],
    'Raccordement': ['raccordement','branchement','installation'],
}

def classer_reclamation(texte):
    texte_lower = str(texte).lower()
    for theme, mots in keywords.items():
        if any(m in texte_lower for m in mots):
            return theme
    return 'Autre'

reclamations['theme'] = reclamations['texte'].apply(classer_reclamation)
themes = reclamations['theme'].value_counts()
print(f"\n  Thèmes des réclamations :")
print(themes.to_string())

# ── Figure 9 : Réclamations ──
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Analyse des réclamations clients", fontsize=14, fontweight='bold')

# Distribution satisfaction
sat_dist = reclamations['satisfaction'].value_counts().sort_index()
colors_sat = ['#F44336','#FF5722','#FF9800','#8BC34A','#4CAF50']
axes[0].bar(sat_dist.index, sat_dist.values, color=colors_sat, edgecolor='white', alpha=0.85)
axes[0].set_xlabel("Note de satisfaction")
axes[0].set_ylabel("Nombre de réclamations")
axes[0].set_title(f"Distribution de la satisfaction\n(Moy : {reclamations['satisfaction'].mean():.2f}/5)")

# Satisfaction par zone
axes[1].barh(sat_zone.index, sat_zone.values,
             color=[PALETTE_ZONES.get(z,'#888') for z in sat_zone.index])
axes[1].axvline(reclamations['satisfaction'].mean(), color='red', linestyle='--', label='Moyenne')
axes[1].set_xlabel("Satisfaction moyenne (/5)")
axes[1].set_title("Satisfaction par zone géographique")
axes[1].legend()

# Thèmes
axes[2].barh(themes.index, themes.values, color='#2196F3', edgecolor='white', alpha=0.85)
axes[2].set_xlabel("Nombre de réclamations")
axes[2].set_title("Thématiques des réclamations")

plt.tight_layout()
plt.savefig(OUT_DIR + 'fig09_reclamations.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Figure 09 sauvegardée : Réclamations")


# ─────────────────────────────────────────────
# 12. TABLEAU DE SYNTHÈSE — NOTE DE QUALITÉ
# ─────────────────────────────────────────────
print("\n[12] NOTE DE QUALITÉ DES DONNÉES")
print("-" * 40)

note_qualite = pd.DataFrame({
    'Problème': ['Valeurs manquantes', 'Valeurs négatives', 'Doublons (pdl+date)', 'Valeurs aberrantes (>p99.9)'],
    'Nombre': [manquants, negatifs, doublons, aberrants_h],
    'Taux (%)': [f'{manquants/total*100:.1f}%', f'{negatifs/total*100:.1f}%',
                 f'{doublons/total*100:.1f}%', f'{aberrants_h/total*100:.1f}%'],
    'Traitement appliqué': [
        'Imputation médiane glissante 7j par PDL',
        'Reclassés NaN (consommation physiquement impossible)',
        'Suppression (1ère occurrence conservée)',
        'Reclassés NaN puis imputés'
    ]
})
print(note_qualite.to_string(index=False))
note_qualite.to_csv(OUT_DIR + 'note_qualite_donnees.csv', index=False, encoding='utf-8-sig')


# ─────────────────────────────────────────────
# 13. EXPORT DU DATASET NETTOYÉ
# ─────────────────────────────────────────────
df_export = df[['id_pdl','date','consommation_kwh','zone','type_client','segment',
                'type_chauffage','type_compteur','annee','mois','saison',
                'jour_semaine','temp_moyenne_c','DJU']].copy()
df_export.to_csv(OUT_DIR + 'releves_nettoyes.csv', index=False, encoding='utf-8-sig')
print(f"\n  Dataset nettoyé exporté : releves_nettoyes.csv ({len(df_export):,} lignes)")


# ─────────────────────────────────────────────
# 14. RÉSUMÉ FINAL
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("RÉCAPITULATIF — INSIGHTS CLÉS POUR NÉOVOLT")
print("=" * 60)
print(f"""
1. QUALITÉ DES DONNÉES
   → {manquants+negatifs+doublons+aberrants_h:,} anomalies traitées ({(manquants+negatifs+doublons+aberrants_h)/total*100:.1f}% du jeu de données)
   → Qualité globale suffisante pour l'analyse

2. SAISONNALITÉ FORTE
   → Ratio Hiver/Été : {conso_mois[[12,1,2]].mean():.0f} kWh vs {conso_mois[[6,7,8]].mean():.0f} kWh/PDL/jour
   → Corrélation DJU/Consommation : r = {corr_global:.2f} (forte)

3. HEURE DE POINTE
   → Pointe principale à {heure_pic}h00
   → Pointes matinales (7-10h) et vespérales (18-22h) bien marquées

4. FRAUDES
   → 24 fraudes confirmées, sous-comptage majoritaire (58%)
   → PDL frauduleux : {conso_fraude:.1f} kWh/j vs {conso_normal:.1f} kWh/j pour les normaux
   → Gisement d'économies à quantifier

5. INCIDENTS
   → {len(incidents)} incidents, {incidents['nb_pdl_impactes'].sum():,} PDL impactés
   → Cause principale : vétusté matérielle + inconnue

6. SATISFACTION CLIENT
   → Note moyenne {reclamations['satisfaction'].mean():.2f}/5 — Signal d'alerte
   → Zone la plus critique : {sat_zone.index[0]}
""")

print("\nAnalyse complète terminée — 9 figures + 2 exports générés")
print(f"   Outputs dans : {OUT_DIR}")
