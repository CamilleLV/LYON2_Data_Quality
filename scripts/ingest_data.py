import pandas as pd
from sqlalchemy import create_engine
import os
import time

# --- CONFIGURATION ---
DB_URI = "postgresql+psycopg2://admin:admin@postgres_warehouse:5432/sirene_dw"
INPUT_FILE = "/opt/airflow/data/StockEtablissement_utf8_100000.csv" # Vérifie le nom !
CHUNK_SIZE = 10000  # On réduit à 10k pour soulager la RAM

def ingest_data():
    print(f"--- 🚀 Démarrage Ingestion du fichier : {INPUT_FILE} ---")
    
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"❌ Fichier introuvable : {INPUT_FILE}")

    engine = create_engine(DB_URI)
    
    # On force tout en string pour éviter que Pandas ne scanne tout pour deviner les types
    # Cela accélère le démarrage et économise la RAM
    iter_csv = pd.read_csv(
        INPUT_FILE, 
        sep=',', 
        dtype=str, 
        chunksize=CHUNK_SIZE,
        low_memory=True
    )

    total_rows = 0
    start_time = time.time()

    for i, chunk in enumerate(iter_csv):
        mode = 'replace' if i == 0 else 'append'
        
        # Insertion
        chunk.to_sql('raw_stock_etablissement', engine, if_exists=mode, index=False)
        
        total_rows += len(chunk)
        
        # Un petit print tous les 10 chunks (100k lignes) pour ne pas spammer les logs
        if i % 10 == 0:
            elapsed = time.time() - start_time
            speed = total_rows / elapsed
            print(f"✅ Chunk {i} traité. Total lignes : {total_rows} ({int(speed)} lignes/sec)")

    print(f"--- 🎉 Ingestion Terminée ! Total : {total_rows} lignes ---")

if __name__ == "__main__":
    ingest_data()