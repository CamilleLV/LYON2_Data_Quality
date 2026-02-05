import pandas as pd
import numpy as np
from sqlalchemy import create_engine

DB_URI = "postgresql+psycopg2://admin:admin@postgres_warehouse:5432/sirene_dw"

def clean_data():
    print("--- Starting Cleaning ---")
    engine = create_engine(DB_URI)
    
    # On lit les données
    df = pd.read_sql("SELECT * FROM raw_stock_etablissement", engine)
    print(f"Loaded {len(df)} raw rows.")

    # 1. Complétude : 
    # (SIRET = on supprime)
    # (Code Postal = on remplit par défaut)
    df.dropna(subset=['siret'], inplace=True)
    df['codePostalEtablissement'] = df['codePostalEtablissement'].fillna('00000')

    # 2. Unicité: Déduplication basé sur le SIRET (on garde le dernier)
    df.drop_duplicates(subset=['siret'], keep='last', inplace=True)

    # 3. Actualité : On supprime les établissements fermés avant l'an 2000.
    # Identification/Marquage des données obsolètes.
    df['dateDernierTraitementEtablissement'] = pd.to_datetime(df['dateDernierTraitementEtablissement'], errors='coerce')
    mask_active = df['etatAdministratifEtablissement'] == 'A'
    mask_recent = (df['etatAdministratifEtablissement'] == 'F') & (df['dateDernierTraitementEtablissement'].dt.year >= 2000)
    df = df[mask_active | mask_recent]

    # 4. Exactitude: Correction des formats invalides (regex).
    df = df[df['siret'].str.match(r'^\d{14}$', na=False)]
    df = df[df['codePostalEtablissement'].str.match(r'^\d{5}$', na=False)]

    # 5. Validité : Codes APE (XX.X ou XX.XX)
    # Conformité aux référentiels métier.
    df = df[df['activitePrincipaleEtablissement'].str.match(r'^\d{2}\.\d{1,2}[A-Z]?$', na=False)]

    # 6. Cohérence : Règles inter-colonnes (temporelles).
    # Creation < Dernier Traitement
    df['dateCreationEtablissement'] = pd.to_datetime(df['dateCreationEtablissement'], errors='coerce')
    mask_consistent = df['dateCreationEtablissement'] <= df['dateDernierTraitementEtablissement']
    df = df[mask_consistent | df['dateDernierTraitementEtablissement'].isna()]

    # On récupère les données nettoyées.
    print(f"Writing {len(df)} cleaned rows to DB...")
    df.to_sql('cleaned_stock_etablissement', engine, if_exists='replace', index=False)
    print("--- Cleaning Complete ---")

if __name__ == "__main__":
    clean_data()