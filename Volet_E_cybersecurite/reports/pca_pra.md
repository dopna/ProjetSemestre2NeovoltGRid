# PCA / PRA – Néovolt Grid+

## 1. Objectif

Garantir la continuité du service et la reprise rapide de la plateforme Néovolt Grid+ en cas d’incident majeur : cyberattaque, panne cloud, corruption de données, ransomware ou indisponibilité de la plateforme Data.

## 2. Périmètre

Le PCA/PRA couvre :

- la plateforme Data Lake ;
- les pipelines d’ingestion ;
- l’API métier ;
- les tableaux de bord ;
- les modèles IA ;
- les journaux de sécurité ;
- les données clients et consommation.

## 3. Scénarios d’incident

| Scénario | Impact | Criticité |
|---|---|---|
| Ransomware plateforme Data | Indisponibilité des données et dashboards | Critique |
| Perte du Data Lake | Perte historique consommation | Critique |
| Indisponibilité API | Interruption des services applicatifs | Élevée |
| Corruption modèle IA | Prévisions erronées | Élevée |
| Fuite données clients | Incident RGPD | Critique |
| Perte des logs | Difficulté d’investigation | Élevée |

## 4. Objectifs de reprise

| Composant | RTO | RPO |
|---|---:|---:|
| API métier | 4 h | 15 min |
| Data Lake | 8 h | 1 h |
| Dashboard décisionnel | 8 h | 1 h |
| Modèle IA | 24 h | 24 h |
| Logs sécurité | 4 h | 15 min |

## 5. Mesures PCA

- Architecture redondée ;
- sauvegardes quotidiennes ;
- sauvegardes immuables contre ransomware ;
- supervision continue ;
- procédure de bascule ;
- journalisation centralisée ;
- documentation des dépendances critiques.

## 6. Mesures PRA

1. Identifier l’incident.
2. Isoler les systèmes compromis.
3. Restaurer les sauvegardes saines.
4. Vérifier l’intégrité des données.
5. Redéployer les services critiques.
6. Rejouer les pipelines si nécessaire.
7. Contrôler les accès.
8. Produire un rapport post-incident.

## 7. Priorisation de reprise

| Priorité | Service |
|---|---|
| P1 | Authentification, logs sécurité, API critique |
| P2 | Data Lake et pipelines |
| P3 | Dashboards métier |
| P4 | Modèles IA |
| P5 | Reporting secondaire |

## 8. Tests du PCA/PRA

Un test de restauration doit être réalisé au minimum deux fois par an.

Tests recommandés :

- restauration d’un backup ;
- simulation ransomware ;
- indisponibilité API ;
- perte partielle du Data Lake ;
- bascule vers environnement secondaire.

## 9. Lien avec le Volet D

Le Volet D doit prévoir une architecture déployable et reproductible.  
Le Volet E complète cette architecture avec :

- sauvegarde ;
- restauration ;
- supervision ;
- journalisation ;
- réponse à incident ;
- continuité d’activité.

## 10. Conclusion

Le PCA/PRA permet à Néovolt de maintenir un niveau de service acceptable malgré un incident majeur.  
Compte tenu du caractère critique de l’infrastructure énergétique, la continuité d’activité doit être pensée dès la conception de la plateforme.