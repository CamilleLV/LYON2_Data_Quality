# Projet Data Quality & Gouvernance - Données SIRENE

Ce projet a été réalisé dans le cadre de notre cursus académique. Il vise à mettre en œuvre une architecture **Data Engineering** complète pour l'ingestion, le nettoyage, la validation et le monitoring de la qualité des données (Data Quality) du répertoire SIRENE (INSEE).

## Auteurs

Projet réalisé par :
* **Camille LAVERIE**
* **Charlène BROUTIER**

---

## Structure du Projet

Voici l'organisation détaillée des fichiers et dossiers du repository :

```text
.
├── .env                                    # Variables d'environnement
├── .gitignore                              # Fichiers ignorés par Git
├── docker-compose.yaml                     # Configuration principale de la stack Docker
├── Dockerfile                              # Image Docker personnalisée
├── requirements.txt                        # Dépendances Python
├── Etude-de-Cas...Donnees.pdf              # Sujet du projet
├── INSTALLATION_ET_PRISE_EN_MAIN.pdf       # Guide d'installation rapide
├── README.md                               # Documentation (Ce fichier)
│
├── Rapports/                               # Rapports détaillés par phase
│   ├── 1_Choix_Du_Dataset.pdf
│   ├── 2_Exploration_Avec_Jupyter.pdf
│   ├── 3_Les_Pilliers_De_La_Data_Quality.pdf
│   ├── 4_Validation_Avec_Great_Expectations.pdf
│   ├── 5_Dataviz_Des_KPI_De_Data_Quality_Avec_Superset.pdf
│   ├── 6_Gouvernance_Avec_OpenMetadata.pdf
│   └── 7_Orchestration_Et_Automatisation_Avec_Airflow.pdf
│
├── dags/                                   # Orchestration Airflow
│   └── data_quality_pipeline.py            # DAG principal (Ingest -> Clean -> Validate)
│
├── dashboards_superset/                    # Exports des Dashboards
│   └── dashboard_export_20260204.zip       # Backup de la configuration Superset
│
├── data/                                   # Données
│   ├── create_sample.py                    # Script de génération d'échantillon
│   ├── StockEtablissement_utf8_100000.csv  # Échantillon de travail (Source)
│   └── StockEtablissement_utf8_sample.csv
│
├── init_db/                                # Initialisation Base de Données
│   └── init.sql                            # Scripts SQL de création des users/DBs
│
├── notebooks/                              # Analyse et Explorations
│   ├── Data_Quality_Profiling.ipynb        # Audit automatique (YData Profiling)
│   ├── exploration_manuelle.ipynb          # Analyse métier approfondie
│   ├── dq_metrics.ipynb                    # Génération des métriques pour le monitoring
│   ├── Great_Expectations.ipynb            # Tests de validation GX
│   ├── rapport_exploration_sirene.html     # Rapport HTML généré
│   └── validation_results.json             # Résultats bruts de validation
│
└── scripts/                                # Scripts ETL appelés par Airflow
    ├── ingest_data.py                      # Ingestion (Raw)
    ├── clean_data.py                       # Nettoyage et Standardisation
    └── validate_data.py                    # Validation Qualité (Great Expectations)

```
## Architecture Technique

Le projet repose sur une architecture conteneurisée via **Docker**, orchestrant les services suivants :

* **Ingestion & ETL :** Scripts Python (Pandas) pour le traitement des CSV.
* **Orchestration :** **Apache Airflow** (Port 8090) pour planifier les tâches.
* **Data Warehouse :** **PostgreSQL** (Port 5432) pour le stockage (Schemas `raw` et `cleaned`).
* **Data Quality :** **Great Expectations** pour la validation des règles métier.
* **Monitoring & BI :** **Apache Superset** (Port 8088) pour les dashboards de qualité.

---

## Installation et Configuration

### Prérequis
* Docker & Docker Compose installés.
* Un terminal (PowerShell, Bash ou CMD).

### 1. Démarrage de la Stack
À la racine du projet, lancez la construction et le démarrage des conteneurs :

```bash 
docker-compose up --build -d
```

### 2. Configuration de Superset (Indispensable)
L'image officielle de Superset nécessite l'installation manuelle du pilote PostgreSQL. Exécutez ces commandes une par une dans votre terminal :

#### A. Installation des pilotes
```bash 
# Installation de pip et curl dans le conteneur
docker-compose exec -u root superset bash -c "apt-get update && apt-get install -y curl && curl -sS [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py) | python"

# Installation du pilote psycopg2
docker-compose exec -u root superset python -m pip install psycopg2-binary

# Vérification
docker-compose exec superset python -c "import psycopg2; print('Driver PostgreSQL OK')"

# Redémarrage du service pour prise en compte
docker-compose restart superset
```

#### B. Initialisation de l'application Une fois le redémarrage terminé (attendre ~30 sec) :
```bash 
# Migration de la base de données interne
docker-compose exec superset superset db upgrade

# Création du compte Admin
docker-compose exec superset superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin

# Initialisation des rôles
docker-compose exec superset superset init
```

#### 3. Configuration des Dépendances Airflow
Pour permettre l'exécution des scripts de validation Great Expectations, installez les paquets requis dans le scheduler :
```bash 
docker-compose exec airflow-scheduler python -m pip install --user "great_expectations==0.18.19" "sqlalchemy<2.0" psycopg2-binary
```

## Connexions aux Outils

### 1. Connecter Superset à la Base de Données
1.  Accédez à **[http://localhost:8088](http://localhost:8088)** (Login: `admin` / Pass: `admin`).
2.  Allez dans **Settings** -> **Database Connections** -> **+ Database**.
3.  Utilisez les paramètres suivants :
    * **Type de Base :** PostgreSQL
    * **SQLAlchemy URI :** `postgresql://admin:admin@postgres_warehouse:5432/sirene_dw`
    * **Display Name :** Sirene

### 2. Connecter Airflow (Variables)
1.  Accédez à **[http://localhost:8090](http://localhost:8090)** (Login: `admin` / Pass: `admin`).
2.  Dans **Admin** -> **Connections**, créez ou modifiez la connexion `sirene_warehouse` :
    * **Connection Type :** Postgres
    * **Host :** `postgres_warehouse`
    * **Login :** `admin`
    * **Password :** *(Laisser vide)*
    * **Schema :** `sirene_dw`
    * **Port :** `5432`

---
## Utilisation du Pipeline

### Lancement du Traitement
Le pipeline est piloté par le DAG `data_quality_pipeline`. Il exécute séquentiellement :
1.  **Ingest :** Chargement des données brutes (CSV vers DB).
2.  **Clean :** Nettoyage, typage (Codes Postaux, Dates) et déduplication.
3.  **Validate :** Vérification de la conformité des données (Validation Great Expectations).

Pour le lancer : Activez le DAG ("Unpause") et cliquez sur le bouton **Trigger DAG** (►) dans l'interface Airflow.

### Monitoring
Une fois les données traitées, les tableaux de bord Superset permettent de visualiser :
* Le score de qualité global.
* Les taux de complétude et d'exactitude.
* L'évolution temporelle de la qualité des données.
* La répartition des motifs de rejet.

---
## Note
Le fichier source complet SIRENE étant trop volumineux pour Git, ce projet est configuré pour utiliser par défaut le fichier `StockEtablissement_utf8_100000.csv` (échantillon représentatif) situé dans le dossier `data/`.
Le système d'alerte n'est pas implémenté dans cette version de Superset, il faudrait à l'avenir prendre en compte ce système dans l'installation du service.

---
