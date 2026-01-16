import pandas as pd
from sqlalchemy import create_engine
import os

# Database Connection (Internal Docker Network)
DB_URI = "mysql+mysqlconnector://admin:admin@mariadb:3306/sirene_dw"
INPUT_FILE = "/opt/airflow/data/StockEtablissement_utf8.csv"
CHUNK_SIZE = 50000

def ingest_data():
    print("--- Starting Ingestion ---")
    engine = create_engine(DB_URI)
    
    # Define types for efficiency
    dtype_map = {
        'siret': str, 'siren': str, 'codePostalEtablissement': str,
        'activitePrincipaleEtablissement': str
    }

    try:
        # Using iterator=True for chunking
        with pd.read_csv(INPUT_FILE, dtype=dtype_map, chunksize=CHUNK_SIZE, low_memory=False) as reader:
            for i, chunk in enumerate(reader):
                if i == 0:
                    # Replace table on first chunk
                    chunk.to_sql('raw_stock_etablissement', engine, if_exists='replace', index=False)
                else:
                    # Append on subsequent chunks
                    chunk.to_sql('raw_stock_etablissement', engine, if_exists='append', index=False)
                print(f"Batch {i+1} loaded.")
        print("--- Ingestion Complete ---")
        
    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
        exit(1)

if __name__ == "__main__":
    ingest_data()