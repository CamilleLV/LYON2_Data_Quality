import pandas as pd
import numpy as np
from sqlalchemy import create_engine

DB_URI = "mysql+mysqlconnector://admin:admin@mariadb:3306/sirene_dw"

def clean_data():
    print("--- Starting Cleaning ---")
    engine = create_engine(DB_URI)
    
    # Read Raw Data
    df = pd.read_sql("SELECT * FROM raw_stock_etablissement", engine)
    print(f"Loaded {len(df)} raw rows.")

    # 1. Completeness: Drop rows without SIRET, fill PostCode
    df.dropna(subset=['siret'], inplace=True)
    df['codePostalEtablissement'] = df['codePostalEtablissement'].fillna('00000')

    # 2. Uniqueness: Dedup on SIRET
    df.drop_duplicates(subset=['siret'], keep='last', inplace=True)

    # 3. Timeliness: Remove closed before 2000
    df['dateDernierTraitementEtablissement'] = pd.to_datetime(df['dateDernierTraitementEtablissement'], errors='coerce')
    mask_active = df['etatAdministratifEtablissement'] == 'A'
    mask_recent = (df['etatAdministratifEtablissement'] == 'F') & (df['dateDernierTraitementEtablissement'].dt.year >= 2000)
    df = df[mask_active | mask_recent]

    # 4. Accuracy: Regex for SIRET (14) and PostCode (5)
    df = df[df['siret'].str.match(r'^\d{14}$', na=False)]
    df = df[df['codePostalEtablissement'].str.match(r'^\d{5}$', na=False)]

    # 5. Validity: APE Codes (XX.X or XX.XX)
    # Simplified regex for demonstration
    df = df[df['activitePrincipaleEtablissement'].str.match(r'^\d{2}\.\d{1,2}[A-Z]?$', na=False)]

    # 6. Consistency: Creation < Last Treatment
    df['dateCreationEtablissement'] = pd.to_datetime(df['dateCreationEtablissement'], errors='coerce')
    mask_consistent = df['dateCreationEtablissement'] <= df['dateDernierTraitementEtablissement']
    df = df[mask_consistent | df['dateDernierTraitementEtablissement'].isna()]

    # Write Cleaned Data
    print(f"Writing {len(df)} cleaned rows to DB...")
    df.to_sql('cleaned_stock_etablissement', engine, if_exists='replace', index=False)
    print("--- Cleaning Complete ---")

if __name__ == "__main__":
    clean_data()