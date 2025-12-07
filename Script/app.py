import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

# Creazione dell'applicazione Flask con percorsi personalizzati per UI
app = Flask(__name__, template_folder='../UI', static_folder='../UI')

# Definisce il percorso del database nella cartella Dati
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '../Dati/gestione.db')

def get_db_connection():
    """Crea una connessione al database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_accounts():
    """Recupera tutti gli account dal database."""
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts ORDER BY name').fetchall()
    conn.close()
    return accounts

def get_data_grouped_by_folder():
    """
    Recupera tutte le app e le unisce con i loro account, raggruppandole per cartella.
    Restituisce un dizionario dove le chiavi sono i nomi delle cartelle.
    """
    conn = get_db_connection()
    # Query aggiornata per ottenere anche l'ID dell'account
    query = """
        SELECT
            a.id as app_id,
            a.name as app_name,
            a.folder as app_folder,
            acc.id as account_id,
            acc.name as account_name
        FROM
            apps a
        LEFT JOIN
            app_accounts aa ON a.id = aa.app_id
        LEFT JOIN
            accounts acc ON aa.account_id = acc.id
        ORDER BY
            a.folder, a.name, acc.name;
    """
    rows = conn.execute(query).fetchall()
    conn.close()

    # Struttura per aggregare i risultati per cartella
    folders_dict = {}

    for row in rows:
        folder_name = row['app_folder']
        app_id = row['app_id']

        if folder_name not in folders_dict:
            folders_dict[folder_name] = {}
        
        if app_id not in folders_dict[folder_name]:
            folders_dict[folder_name][app_id] = {
                'id': app_id,
                'name': row['app_name'],
                'accounts': []
            }
        
        # Aggiungiamo l'account (con id e nome) alla lista dell'app, se esiste
        if row['account_id'] and row['account_name']:
            # Evita duplicati se un'app senza account appare più volte (improbabile con LEFT JOIN)
            account_data = {'id': row['account_id'], 'name': row['account_name']}
            if account_data not in folders_dict[folder_name][app_id]['accounts']:
                folders_dict[folder_name][app_id]['accounts'].append(account_data)

    # Convertiamo i dizionari di app interni in liste
    final_structure = {}
    for folder, apps in folders_dict.items():
        final_structure[folder] = list(apps.values())
        
    return final_structure


@app.route('/')
def index():
    """
    Pagina principale che visualizza l'elenco di tutte le app, raggruppate per cartella.
    """
    apps_by_folder = get_data_grouped_by_folder()
    all_accounts = get_all_accounts()
    return render_template('index.html', apps_by_folder=apps_by_folder, all_accounts=all_accounts)

@app.route('/add_account', methods=['POST'])
def add_account():
    """
    Aggiunge un'associazione tra un'app e un account nel database.
    """
    app_id = request.form.get('app_id')
    account_id = request.form.get('account_id')

    if app_id and account_id:
        conn = get_db_connection()
        conn.execute(
            'INSERT OR IGNORE INTO app_accounts (app_id, account_id) VALUES (?, ?)',
            (app_id, account_id)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('index'))

@app.route('/remove_account', methods=['POST'])
def remove_account():
    """
    Rimuove un'associazione tra un'app e un account dal database.
    """
    app_id = request.form.get('app_id')
    account_id = request.form.get('account_id')

    if app_id and account_id:
        conn = get_db_connection()
        conn.execute(
            'DELETE FROM app_accounts WHERE app_id = ? AND account_id = ?',
            (app_id, account_id)
        )
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
