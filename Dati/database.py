import sqlite3
import os

# Il database si troverà nella stessa cartella di questo script
DB_FILE = os.path.join(os.path.dirname(__file__), 'gestione.db')

def init_db():
    """
    Crea e inizializza il database con le tabelle necessarie se non esistono già.
    Le tabelle sono:
    - accounts: contiene le informazioni sugli account (es. indirizzi email).
    - apps: contiene i nomi delle app e la cartella in cui si trovano.
    - app_accounts: tabella di collegamento per la relazione molti-a-molti tra app e account.
    """
    try:
        # Si connette al database (lo crea se non esiste)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Creazione tabella 'accounts'
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            abbreviation TEXT
        );
        """)

        # Aggiungi colonne 'order' e 'is_hidden' alla tabella 'accounts' se non esistono
        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN 'order' INTEGER DEFAULT 0;")
            print("Colonna 'order' aggiunta alla tabella 'accounts'.")
        except sqlite3.OperationalError:
            pass # Colonna già esistente
        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN is_hidden INTEGER DEFAULT 0;")
            print("Colonna 'is_hidden' aggiunta alla tabella 'accounts'.")
        except sqlite3.OperationalError:
            pass # Colonna già esistente

        # Creazione tabella 'apps'
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            folder TEXT NOT NULL
        );
        """)

        # Aggiungi colonne 'order' e 'is_hidden' alla tabella 'apps' se non esistono
        try:
            cursor.execute("ALTER TABLE apps ADD COLUMN 'order' INTEGER DEFAULT 0;")
            print("Colonna 'order' aggiunta alla tabella 'apps'.")
        except sqlite3.OperationalError:
            pass # Colonna già esistente
        try:
            cursor.execute("ALTER TABLE apps ADD COLUMN is_hidden INTEGER DEFAULT 0;")
            print("Colonna 'is_hidden' aggiunta alla tabella 'apps'.")
        except sqlite3.OperationalError:
            pass # Colonna già esistente

        # Creazione tabella di collegamento 'app_accounts'
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_accounts (
            app_id INTEGER,
            account_id INTEGER,
            FOREIGN KEY (app_id) REFERENCES apps (id),
            FOREIGN KEY (account_id) REFERENCES accounts (id),
            PRIMARY KEY (app_id, account_id)
        );
        """)

        conn.commit()
        print(f"Database '{DB_FILE}' creato e tabelle inizializzate con successo.")

    except sqlite3.Error as e:
        print(f"Errore durante l'inizializzazione del database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Inizializzazione del database...")
    init_db()
