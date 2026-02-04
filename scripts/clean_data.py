from sqlalchemy import create_engine, text

DB_URI = "postgresql+psycopg2://admin:admin@postgres_warehouse:5432/sirene_dw"

def clean_data():
    print("--- 🧹 Démarrage du Nettoyage (Mode SQL In-Database) ---")
    engine = create_engine(DB_URI)

    # On utilise une connexion brute pour exécuter du SQL complexe
    with engine.connect() as conn:
        
        # 0. Création de la table propre (vide pour l'instant)
        print("1. Préparation de la table cleaned...")
        conn.execute(text("DROP TABLE IF EXISTS cleaned_stock_etablissement"))
        
        # C'est ici que la magie opère : CREATE TABLE AS SELECT ...
        # On traduit tes règles Pandas en SQL
        query = text("""
            CREATE TABLE cleaned_stock_etablissement AS
            SELECT 
                siret,
                -- Règle 1 (Complétude) : Remplacer Code Postal vide par 00000
                COALESCE("codePostalEtablissement", '00000') as "codePostalEtablissement",
                "activitePrincipaleEtablissement",
                "dateCreationEtablissement",
                "dateDernierTraitementEtablissement",
                "etatAdministratifEtablissement"
            FROM raw_stock_etablissement
            WHERE 
                -- Règle 1 (Complétude) : SIRET doit exister
                siret IS NOT NULL
                
                -- Règle 4 (Exactitude) : Regex SIRET (14 chiffres)
                AND siret ~ '^\d{14}$'
                
                -- Règle 4 (Exactitude) : Regex Code Postal (5 chiffres)
                AND "codePostalEtablissement" ~ '^\d{5}$'
                
                -- Règle 5 (Validité) : Format APE (ex: 62.01Z)
                AND "activitePrincipaleEtablissement" ~ '^\d{2}\.\d{1,2}[A-Z]?$'
                
                -- Règle 3 (Actualité) : Actif OU (Fermé après 2000)
                AND (
                    "etatAdministratifEtablissement" = 'A'
                    OR (
                        "etatAdministratifEtablissement" = 'F' 
                        AND "dateDernierTraitementEtablissement" >= '2000-01-01'
                    )
                )
                
                -- Règle 6 (Cohérence) : Création <= Dernier Traitement
                AND (
                    "dateCreationEtablissement" <= "dateDernierTraitementEtablissement"
                    OR "dateDernierTraitementEtablissement" IS NULL
                );
        """)
        conn.execute(query)
        
        # Règle 2 (Unicité) : Postgres ne gère pas le "drop_duplicates" facilement à la création
        # On va donc garder une seule ligne par SIRET (la plus récente si doublon)
        print("2. Dédoublonnage final (Unicité)...")
        
        # On crée une table temporaire pour supprimer les doublons
        dedup_query = text("""
            DELETE FROM cleaned_stock_etablissement a USING (
                SELECT min(ctid) as ctid, siret
                FROM cleaned_stock_etablissement 
                GROUP BY siret HAVING COUNT(*) > 1
            ) b
            WHERE a.siret = b.siret 
            AND a.ctid <> b.ctid
        """)
        conn.execute(dedup_query)

    print("--- ✨ Nettoyage Terminé ! ---")

if __name__ == "__main__":
    clean_data()