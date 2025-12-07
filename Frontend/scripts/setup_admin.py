import sqlite3
import os
import getpass
from werkzeug.security import generate_password_hash

# Definisce il percorso del database
# Assumendo che setup_admin.py sia nella root del progetto (HTML/)
# e il DB in Dati/mdb-database/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'Dati/mdb-database/gestione.db')

def setup_admin_user():
    """
    Script per configurare l'utente amministratore iniziale 'piccolacleo'.
    Chiede una password e la salva hashed nel database.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        admin_username = "piccolacleo"

        # Controlla se l'utente esiste già
        cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
        user_exists = cursor.fetchone()

        if user_exists:
            print(f"L'utente amministratore '{admin_username}' esiste già. Nessuna modifica apportata.")
            return

        print(f"Configurazione dell'utente amministratore '{admin_username}'.")
        while True:
            password = getpass.getpass("Inserisci la password per l'utente amministratore: ")
            confirm_password = getpass.getpass("Conferma la password: ")

            if password == confirm_password:
                if not password:
                    print("La password non può essere vuota. Riprova.")
                    continue
                hashed_password = generate_password_hash(password)
                break
            else:
                print("Le password non corrispondono. Riprova.")
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (admin_username, hashed_password, 1)
        )
        conn.commit()
        print(f"Utente amministratore '{admin_username}' creato con successo.")

    except sqlite3.Error as e:
        print(f"Errore durante la configurazione dell'utente amministratore: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Avvio script di configurazione amministratore...")
    setup_admin_user()