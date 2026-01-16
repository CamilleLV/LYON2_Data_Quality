# Projet Gouvernance & Qualité des Données - Université Lyon 2

Ce projet a été réalisé dans le cadre du cours de **Gouvernance de la Donnée**. Il vise à mettre en place un pipeline de traitement, de nettoyage et de validation de données (Data Quality) sur la base de données des établissements français (SIRENE).

## 📋 Description

L'objectif est d'orchestrer un flux de données complet incluant :
1.  **Exploration** des données brutes.
2.  **Nettoyage** et standardisation (Data Cleaning).
3.  **Validation** de la qualité des données (règles métiers, complétude, unicité).
4.  **Ingestion** dans une base de données structurée.

## 🛠 Architecture du projet

L'architecture repose sur **Docker** pour garantir la portabilité de l'environnement.

```text
LYON2_Data_Quality/
├── dags/                  # Dags Airflow pour l'orchestration du pipeline
│   └── data_quality_pipeline.py
├── data/                  # Dossier de stockage des données (local)
│   └── StockEtablissement_utf8.csv  (Non versionné, voir Installation)
├── init_db/               # Scripts d'initialisation de la Base de Données
│   └── init.sql
├── notebooks/             # Notebooks Jupyter pour l'analyse exploratoire
│   └── exploration.ipynb
├── scripts/               # Scripts Python modulaires
│   ├── clean_data.py      # Logique de nettoyage
│   ├── ingest_data.py     # Script d'ingestion en base
│   └── validate_data.py   # Tests de qualité (Data Quality checks)
├── Dockerfile             # Définition de l'image Python/App
├── docker-compose.yaml    # Orchestration des conteneurs (App, DB, etc.)
├── requirements.txt       # Dépendances Python
└── README.md              # Documentation du projet
