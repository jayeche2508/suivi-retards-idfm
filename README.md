# Suivi des Retards de Transport - API IDFM

Projet de conception d'un outil de suivi en temps réel et de stockage des retards des trains (RER D) à partir de l'open data francilienne.

## Description

Ce projet consiste à interroger l'API publique d'Île-de-France Mobilités pour récupérer les horaires des prochains passages, calculer l'écart entre l'horaire théorique et l'horaire estimé, puis alimenter automatiquement une base de données relationnelle pour constituer un historique des retards.

## Étapes réalisées

1. **Création de la base de données (PostgreSQL) :** création d'une table `passages` destinée à stocker l'historique continu des trains ( `ligne` , `destination` , `heure_theorique` , `heure_estimee` , `retard_minutes` ).
2. **Script de collecte en temps réel :** appel HTTP vers l'API PRIM avec `requests` , parsing du JSON, calcul du retard, et gestion des horaires non communiqués en fin de service avant l'insertion automatique en base via `psycopg2` .
3. **Sécurisation :** masquage de la clé API et des identifiants de la base de données via un fichier `.env` pour éviter l'exposition des données sensibles.

## Technologies utilisées

* PostgreSQL
* Python (requests, psycopg2, python-dotenv)
* API REST (SIRI / JSON)
* Visual Studio Code

## Fichiers sources exploités

Le projet exploite les données ouvertes d'Île-de-France Mobilités (Portail PRIM) via l'API **StopMonitoring (SIRI)** pour obtenir les prochains passages par zone d'arrêt en temps réel.

## Lancer le projet

```bash

pip install requests psycopg2-binary python-dotenv

python main.py
