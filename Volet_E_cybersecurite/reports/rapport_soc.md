# Rapport SOC – Néovolt Grid+
## 1. Objectif
Mettre en place une première capacité de supervision sécurité sur les journaux de Néovolt.
## 2. Données analysées
Fichier analysé : journaux_securite.csv

## 3. Règles de détection

| Règle | Description | Criticité |
|---|---|---|
| BRUTE_FORCE | Connexions échouées répétées | Haute |
| ACCES_REFUSES_REPETES | Accès refusés multiples | Moyenne |
| EXPORT_DONNEES | Export de données réussi | Haute |
| MODIFICATION_CONFIG | Modification de configuration | Critique |
| ACTIVITE_SCADA | Activité sur système SCADA | Critique |
| ACTIVITE_PRESTATAIRE | Activité prestataire externe | Haute |

## 4. Résultats

Insérer ici les chiffres obtenus dans le terminal.

## 5. Analyse

Les alertes critiques concernent prioritairement les modifications de configuration et les activités sur les systèmes SCADA. Ces événements doivent être traités en priorité car ils peuvent impacter la continuité du service énergétique.

## 6. Recommandations

- Activer le MFA pour les comptes sensibles.
- Journaliser toutes les actions administrateur.
- Mettre en place un SIEM centralisé.
- Isoler les environnements critiques.
- Mettre en place un runbook de réponse à incident.

***return du script*** 
Répartition des alertes :
type_alerte
ACTIVITE_SCADA          6868
ACTIVITE_PRESTATAIRE    3412
EXPORT_DONNEES          1436
MODIFICATION_CONFIG      973
BRUTE_FORCE                1
Name: count, dtype: int64