# Plan de monitoring MLOps — Néovolt Grid+

## Objectif
Garantir que le modèle de prévision de consommation reste fiable dans le temps.

## Indicateurs à suivre
- RMSE mensuel sur les nouvelles données
- MAE mensuelle
- Dérive de température moyenne par zone
- Dérive de consommation moyenne par compteur
- Taux de valeurs manquantes

## Seuils d'alerte
- RMSE supérieur de 20 % à la performance de référence
- Plus de 5 % de valeurs manquantes sur les variables météo
- Changement brutal de distribution sur la consommation

## Actions correctives
- Analyse de la dérive
- Réentraînement du modèle
- Validation métier
- Redéploiement du modèle validé
