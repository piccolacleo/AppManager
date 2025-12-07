import pandas as pd
import sqlite3
import os
import sys

# Aggiunge la directory dello script al path per permettere l'import di 'database'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Definisce i percorsi relativi alla posizione dello script
BASE_DIR = os.path.dirname(__file__)
XLSX_FILE = os.path.join(BASE_DIR, 'AppCell.xlsx')
DB_FILE = os.path.join(BASE_DIR, 'gestione.db')

def import_data():
    """
    Legge i dati dal file AppCell.xlsx e li importa nel database SQLite.
    - Legge il foglio 'Account' e popola la tabella 'accounts'.
    - Legge il foglio 'POCO' e popola la tabella 'apps'.
    """
    if not os.path.exists(XLSX_FILE):
        print(f"ERRORE: Il file '{XLSX_FILE}' non è stato trovato. Assicurati che sia nella stessa cartella.")
        return

    conn = None  # Inizializza conn a None per un corretto error handling
    try:
        # --- Importazione Account ---
        # Colonne corrette: 'indirizzo email', 'abbreviazione'
        df_accounts = pd.read_excel(XLSX_FILE, sheet_name='Account')
        df_accounts = df_accounts[['indirizzo email', 'abbreviazione']].dropna(subset=['indirizzo email'])

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Inserisce gli account nel database
        for index, row in df_accounts.iterrows():
            try:
                cursor.execute("INSERT INTO accounts (name, abbreviation) VALUES (?, ?)", 
                               (row['indirizzo email'], row['abbreviazione']))
            except sqlite3.IntegrityError:
                print(f"Account '{row['indirizzo email']}' già presente, saltato.")
        
        print(f"Importati {len(df_accounts)} account dal foglio 'Account'.")

        # --- Importazione App ---
        # Colonne corrette: 'Nome App', 'Cartella'
        df_apps = pd.read_excel(XLSX_FILE, sheet_name='POCO')

        apps_imported_count = 0
        for index, row in df_apps.iterrows():
            app_name = row.get('Nome App')
            folder_name = row.get('Cartella', 'Senza cartella')

            if not isinstance(app_name, str) or not app_name.strip():
                print(f"ATTENZIONE: Trovata una riga senza nome app nella cartella '{folder_name}'. Riga saltata.")
                continue
            
            if folder_name == 'Telefono':
                folder_name = 'Schermata Principale'

            try:
                cursor.execute("INSERT INTO apps (name, folder) VALUES (?, ?)", 
                               (app_name.strip(), str(folder_name).strip()))
                apps_imported_count += 1
            except sqlite3.IntegrityError:
                print(f"Applicazione '{app_name}' già presente, saltata.")

        conn.commit()
        print(f"Importate {apps_imported_count} app dal foglio 'POCO'.")

    except Exception as e:
        print(f"Si è verificato un errore durante l'importazione dei dati: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    from database import init_db
    print("Step 1: Inizializzazione del database...")
    # init_db() cancella il db esistente. Eseguiamolo per essere sicuri di ripartire da zero.
    init_db()
    
    print("\nStep 2: Importazione dei dati da Excel...")
    import_data()
    print("\nProcesso completato.")