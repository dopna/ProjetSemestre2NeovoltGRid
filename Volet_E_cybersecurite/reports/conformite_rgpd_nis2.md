# Conformité RGPD, NIS2 et Infrastructure Critique

## 1. Contexte

Néovolt exploite un réseau de distribution d'énergie et traite des données personnelles de plus de 600 000 clients.

Le programme Grid+ collecte, stocke et analyse :

- données clients ;
- données de consommation ;
- données techniques réseau ;
- journaux de sécurité ;
- données issues des compteurs communicants.

Ces traitements doivent respecter les exigences du RGPD ainsi que les obligations de cybersécurité applicables aux opérateurs d'infrastructures critiques.

---

# 2. Analyse RGPD

## Données personnelles traitées

| Donnée | Catégorie |
|----------|----------|
| Nom | Identité |
| Prénom | Identité |
| Adresse | Coordonnée |
| Email | Coordonnée |
| Téléphone | Coordonnée |
| Consommation énergétique | Donnée personnelle |
| Historique de consommation | Donnée personnelle |
| Adresse IP | Donnée technique |

---

## Principes RGPD appliqués

### Licéité

Les traitements reposent sur :

- contrat de fourniture d'énergie ;
- obligation légale ;
- intérêt légitime.

### Minimisation

Seules les données nécessaires sont collectées.

### Exactitude

Les données doivent être maintenues à jour.

### Limitation de conservation

Les données sont supprimées à l'expiration des durées légales.

### Intégrité et confidentialité

Les données sont protégées par :

- chiffrement ;
- contrôle d'accès ;
- journalisation.

---

## Droits des personnes

Néovolt doit permettre :

- droit d'accès ;
- droit de rectification ;
- droit à l'effacement ;
- droit d'opposition ;
- droit à la portabilité.

---

## Registre des traitements

Un registre doit être tenu pour :

- gestion clients ;
- relevés de consommation ;
- détection d'anomalies ;
- prévision énergétique ;
- supervision sécurité.

---

## AIPD

Une Analyse d'Impact relative à la Protection des Données est recommandée car :

- traitement massif ;
- suivi régulier des consommations ;
- usage d'algorithmes de Machine Learning.

---

# 3. Conformité NIS2

## Pourquoi NIS2 ?

Le secteur de l'énergie est explicitement concerné par la directive NIS2.

Néovolt doit mettre en place :

- gouvernance cybersécurité ;
- gestion des risques ;
- supervision continue ;
- réponse à incident ;
- continuité d'activité.

---

## Mesures mises en œuvre

### Gestion des accès

- MFA administrateurs
- RBAC
- revue des comptes

### Journalisation

- logs centralisés
- conservation sécurisée

### Détection

- SOC développé dans le Volet E
- alertes automatiques

### Réponse

- runbook incident
- PCA/PRA

### DevSecOps

- Bandit
- Safety
- GitHub Actions

---

# 4. Classification des données

| Niveau | Exemple |
|----------|----------|
| Public | Communication externe |
| Interne | Procédures internes |
| Confidentiel | Données clients |
| Critique | Réseau énergétique, SCADA, comptes administrateurs |

---

# 5. Mesures de sécurité recommandées

## Mesures techniques

- MFA
- chiffrement AES-256
- TLS 1.3
- segmentation réseau
- EDR
- sauvegardes immuables

## Mesures organisationnelles

- sensibilisation annuelle
- audits sécurité
- revue des habilitations
- exercices PCA/PRA

---

# 6. Rôle des acteurs

| Acteur | Responsabilité |
|----------|----------|
| RSSI | Gouvernance sécurité |
| DPO | Conformité RGPD |
| DSI | Infrastructure |
| Exploitation Réseau | Données techniques |
| Direction | Validation des risques |

---

# 7. Conclusion

Le programme Grid+ respecte les principes du RGPD et s'aligne sur les exigences de la directive NIS2.

Les dispositifs mis en place dans le Volet E permettent :

- la détection des incidents ;
- la protection des données ;
- la continuité des activités ;
- la conformité réglementaire.

La cybersécurité est intégrée dès la conception de la plateforme conformément aux principes de Security by Design et Privacy by Design.