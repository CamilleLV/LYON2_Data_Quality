-- Users et Bases pour les outils
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow;
ALTER DATABASE airflow OWNER TO airflow;

CREATE USER superset WITH PASSWORD 'superset';
CREATE DATABASE superset;
ALTER DATABASE superset OWNER TO superset;

CREATE USER openmetadata_user WITH PASSWORD 'openmetadata_password';
CREATE DATABASE openmetadata_db;
ALTER DATABASE openmetadata_db OWNER TO openmetadata_user;

-- La base sirene_dw est créée automatiquement par Docker via POSTGRES_DB
GRANT ALL PRIVILEGES ON DATABASE sirene_dw TO admin;