# Suivi des Retards de Transport - API IDFM

Projet de conception d'un pipeline de collecte, de traitement et de stockage en temps réel des retards du RER D à partir de l'open data francilienne.

## Description

Ce projet interroge l'API publique d'Île-de-France Mobilités pour récupérer en temps réel les horaires des prochains passages du RER D, calcule l'écart entre les horaires théoriques et réels, puis alimente automatiquement une base de données relationnelle PostgreSQL pour constituer un historique d'exploitation.

## Étapes réalisées

1. **Création de la base de données (PostgreSQL) :** modélisation et création de la table `passages` destinée à enregistrer chaque passage ( `ligne` , `destination` , `heure_theorique` , `heure_estimee` , `retard_minutes` ).
2. **Script de collecte et traitement en temps réel :** requêtage de l'API PRIM avec `requests` , extraction des structures JSON (SIRI), conversion des formats temporels ISO 8601 et calcul du retard en minutes via `datetime` .
3. **Gestion des cas limites :** filtrage automatisé pour ignorer les trains sans estimations d'horaires (fins de service, terminus ou interruptions techniques) afin d'éviter l'insertion d'enregistrements incomplets.
4. **Sécurisation :** externalisation de la clé d'API et des identifiants de connexion dans un fichier `.env` exclu du suivi de versions via `.gitignore` .

## Technologies utilisées

* PostgreSQL
* Python (requests, psycopg2, python-dotenv)
* API REST (Format SIRI / JSON)
* Visual Studio Code

## Données et API exploitées

* `API StopMonitoring (SIRI)` — Flux en temps réel des prochains passages par zone d'arrêt (Portail PRIM d'Île-de-France Mobilités).

## Lancer le projet

### 1. Prérequis
* Un serveur PostgreSQL avec une base nommée `idfm_tracker`.
* Une clé d'API active obtenue gratuitement sur le portail [PRIM d'IDFM](https://prim.iledefrance-mobilites.fr/) (API Stop Monitoring).

### 2. Initialisation de la table SQL
```sql
CREATE TABLE passages (
    id SERIAL PRIMARY KEY,
    ligne VARCHAR(50),
    destination VARCHAR(100),
    heure_theorique TIMESTAMP,
    heure_estimee TIMESTAMP,
    retard_minutes INTEGER
);
```

### 3. Installation et configuration
```bash
# Installer les dépendances
pip install requests psycopg2-binary python-dotenv
```

Créer un fichier `.env` à la racine du projet :
```env
IDFM_API_KEY=votre_cle_api_idfm
DB_PASSWORD=votre_mot_de_passe_postgres
```

### 4. Exécution
```bash
python main.py
```

> **Disponibilité des données :** L'API IDFM fournit des horaires estimés uniquement pendant les plages de circulation active des trains. En période nocturne, en fin de service ou lors de travaux, l'API ne transmet pas d'estimation horaire ; le script ignore alors automatiquement ces passages pour préserver la cohérence des données en base.

## Auteur

* Jayeche CAROUNAGARANE
