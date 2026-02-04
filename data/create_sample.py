import pandas as pd

# --- CONFIGURATION ---
INPUT_FILE = './data/StockEtablissement_utf8_big.csv'  # Ton fichier source géant
OUTPUT_FILE = './data/StockEtablissement_utf8_100000.csv' # Le petit fichier à créer
NB_ROWS = 100000  # Nombre de lignes à garder (suffisant pour tester)

print(f"⏳ Lecture des {NB_ROWS} premières lignes de {INPUT_FILE}...")

try:
    # On utilise nrows pour ne charger que le début du fichier (très rapide)
    # dtype=str évite les avertissements sur les types de colonnes
    df = pd.read_csv(INPUT_FILE, nrows=NB_ROWS, dtype=str)
    
    # On sauvegarde le petit fichier
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"✅ Succès ! Fichier créé : {OUTPUT_FILE}")
    print(f"📊 Dimensions du sample : {df.shape}")

except FileNotFoundError:
    print(f"❌ Erreur : Le fichier '{INPUT_FILE}' est introuvable dans ce dossier.")
except Exception as e:
    print(f"❌ Une erreur est survenue : {e}")