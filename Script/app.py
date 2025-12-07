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

    """Recupera tutti gli account dal database, inclusi order e is_hidden, ordinati per order e nome."""

    conn = get_db_connection()

    accounts = conn.execute('SELECT id, name, abbreviation, "order", is_hidden FROM accounts ORDER BY "order", name').fetchall()

    conn.close()

    return accounts



def get_all_apps():

    """Recupera tutte le app dal database, inclusi order e is_hidden, ordinati per order e nome."""

    conn = get_db_connection()

    apps = conn.execute('SELECT id, name, folder, "order", is_hidden FROM apps ORDER BY "order", name').fetchall()

    conn.close()

    return apps



def get_data_grouped_by_folder():

    """

    Recupera tutte le app e le unisce con i loro account, raggruppandole per cartella.

    Filtra le app e gli account nascosti, ordina per ordine personalizzato e nome.

    Restituisce un dizionario dove le chiavi sono i nomi delle cartelle.

    """

    conn = get_db_connection()

    query = """

        SELECT

            a.id as app_id,

            a.name as app_name,

            a.folder as app_folder,

            a."order" as app_order,

            a.is_hidden as app_is_hidden,

            acc.id as account_id,

            acc.name as account_name,

            acc."order" as account_order,

            acc.is_hidden as account_is_hidden

        FROM

            apps a

        LEFT JOIN

            app_accounts aa ON a.id = aa.app_id

        LEFT JOIN

            accounts acc ON aa.account_id = acc.id

        WHERE

            a.is_hidden = 0 AND (acc.is_hidden = 0 OR acc.is_hidden IS NULL)

        ORDER BY

            a."order", a.name, acc."order", acc.name;

    """

    rows = conn.execute(query).fetchall()

    conn.close()



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

                'folder': row['app_folder'],

                'order': row['app_order'],

                'is_hidden': row['app_is_hidden'],

                'accounts': []

            }

        

        if row['account_id'] and row['account_name']:

            account_data = {

                'id': row['account_id'],

                'name': row['account_name'],

                'order': row['account_order'],

                'is_hidden': row['account_is_hidden']

            }

            if account_data not in folders_dict[folder_name][app_id]['accounts']:

                folders_dict[folder_name][app_id]['accounts'].append(account_data)



    final_structure = {}

    for folder, apps in folders_dict.items():

        # Ordina le app all'interno della cartella prima di convertirle in lista

        sorted_apps = sorted(apps.values(), key=lambda x: (x['order'], x['name']))

        # Ordina gli account all'interno di ciascuna app

        for app_data in sorted_apps:

            if 'accounts' in app_data and app_data['accounts']:

                app_data['accounts'] = sorted(app_data['accounts'], key=lambda x: (x['order'], x['name']))

        final_structure[folder] = sorted_apps

        

    return final_structure





@app.route('/')

def index():

    """

    Pagina principale che visualizza l'elenco di tutte le app, raggruppate per cartella.

    """

    apps_by_folder = get_data_grouped_by_folder()

    all_accounts = get_all_accounts() # Usato per la dropdown in index.html, non dovrebbe filtrare gli hidden

    return render_template('index.html', apps_by_folder=apps_by_folder, all_accounts=all_accounts)



@app.route('/manage')

def manage():

    """

    Pagina per la gestione di app e account.

    """

    all_accounts = get_all_accounts()

    all_apps = get_all_apps()

    return render_template('manage.html', all_accounts=all_accounts, all_apps=all_apps)



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



@app.route('/add_new_account', methods=['POST'])

def add_new_account():

    """

    Aggiunge un nuovo account al database.

    """

    name = request.form.get('name')

    abbreviation = request.form.get('abbreviation')



    if name:

        conn = get_db_connection()

        try:

            conn.execute(

                'INSERT INTO accounts (name, abbreviation) VALUES (?, ?)',

                (name, abbreviation if abbreviation else None)

            )

            conn.commit()

        except sqlite3.IntegrityError:

            pass

        finally:

            conn.close()



    return redirect(url_for('manage'))



@app.route('/delete_account/<int:account_id>', methods=['POST'])

def delete_account(account_id):

    """

    Elimina un account e tutte le sue associazioni.

    """

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute('DELETE FROM app_accounts WHERE account_id = ?', (account_id,))

        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))

        conn.commit()

    except sqlite3.Error as e:

        print(f"Errore durante l'eliminazione dell'account: {e}")

        conn.rollback()

    finally:

        conn.close()

    

    return redirect(url_for('manage'))



@app.route('/update_account_settings', methods=['POST'])

def update_account_settings():

    """

    Aggiorna le impostazioni (ordine, visibilità) di un account.

    """

    account_id = request.form.get('id', type=int)

    order = request.form.get('order', type=int)

    is_hidden = 1 if request.form.get('is_hidden') == 'on' else 0



    if account_id is not None:

        conn = get_db_connection()

        try:

            conn.execute(

                'UPDATE accounts SET "order" = ?, is_hidden = ? WHERE id = ?',

                (order, is_hidden, account_id)

            )

            conn.commit()

        except sqlite3.Error as e:

            print(f"Errore durante l'aggiornamento dell'account: {e}")

            conn.rollback()

        finally:

            conn.close()

            

    return redirect(url_for('manage'))



@app.route('/add_new_app', methods=['POST'])

def add_new_app():

    """

    Aggiunge una nuova applicazione al database.

    """

    name = request.form.get('name')

    folder = request.form.get('folder')



    if name and folder:

        conn = get_db_connection()

        try:

            conn.execute(

                'INSERT INTO apps (name, folder) VALUES (?, ?)',

                (name, folder)

            )

            conn.commit()

        except sqlite3.IntegrityError:

            pass

        finally:

            conn.close()



    return redirect(url_for('manage'))



@app.route('/delete_app/<int:app_id>', methods=['POST'])

def delete_app(app_id):

    """

    Elimina un'applicazione e tutte le sue associazioni.

    """

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute('DELETE FROM app_accounts WHERE app_id = ?', (app_id,))

        cursor.execute('DELETE FROM apps WHERE id = ?', (app_id,))

        conn.commit()

    except sqlite3.Error as e:

        print(f"Errore durante l'eliminazione dell'app: {e}")

        conn.rollback()

    finally:

        conn.close()

    

    return redirect(url_for('manage'))



@app.route('/update_app_settings', methods=['POST'])

def update_app_settings():

    """

    Aggiorna le impostazioni (ordine, visibilità) di un'applicazione.

    """

    app_id = request.form.get('id', type=int)

    order = request.form.get('order', type=int)

    is_hidden = 1 if request.form.get('is_hidden') == 'on' else 0



    if app_id is not None:

        conn = get_db_connection()

        try:

            conn.execute(

                'UPDATE apps SET "order" = ?, is_hidden = ? WHERE id = ?',

                (order, is_hidden, app_id)

            )

            conn.commit()

        except sqlite3.Error as e:

            print(f"Errore durante l'aggiornamento dell'app: {e}")

            conn.rollback()

        finally:

            conn.close()

            

    return redirect(url_for('manage'))





if __name__ == '__main__':

    app.run(debug=True)


    
    
