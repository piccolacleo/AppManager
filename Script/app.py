import sqlite3
import os
from flask import Flask, request, jsonify # Removed render_template, redirect, url_for, session, flash
from flask_cors import CORS # New import for CORS
from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps # Removed as login_required is removed temporarily

# Creazione dell'applicazione Flask
app = Flask(__name__) # Removed template_folder and static_folder as we are creating an API
CORS(app) # Enable CORS for all routes
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24)) # Usa una chiave sicura per le sessioni

# Definisce il percorso del database nella cartella Dati
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '../Dati/gestione.db')

def get_db_connection():
    """Crea una connessione al database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_id(user_id):
    """Recupera un utente dal database tramite ID."""
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,)).fetchone() # Do not return password_hash
    conn.close()
    return user

def get_user_by_username(username):
    """Recupera un utente dal database tramite username."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

# login_required decorator is removed temporarily as we are moving to token-based auth

def get_all_accounts():
    """Recupera tutti gli account dal database, inclusi order e is_hidden, ordinati per order e nome."""
    conn = get_db_connection()
    accounts = conn.execute('SELECT id, name, abbreviation, "order", is_hidden FROM accounts ORDER BY "order", name').fetchall()
    conn.close()
    return [dict(acc) for acc in accounts]

def get_all_apps():
    """Recupera tutte le app dal database, inclusi order e is_hidden, ordinati per order e nome."""
    conn = get_db_connection()
    apps = conn.execute('SELECT id, name, folder, "order", is_hidden FROM apps ORDER BY "order", name').fetchall()
    conn.close()
    return [dict(app) for app in apps]

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
        sorted_apps = sorted(apps.values(), key=lambda x: (x['order'], x['name']))
        for app_data in sorted_apps:
            if 'accounts' in app_data and app_data['accounts']:
                app_data['accounts'] = sorted(app_data['accounts'], key=lambda x: (x['order'], x['name']))
        final_structure[folder] = sorted_apps
        
    return final_structure


@app.route('/api/apps') # Changed route
def get_apps_data(): # Changed function name
    """
    API endpoint che restituisce l'elenco di tutte le app, raggruppate per cartella, come JSON.
    """
    apps_by_folder = get_data_grouped_by_folder()
    return jsonify(apps_by_folder) # Return JSON

@app.route('/api/manage/data') # Changed route
# @login_required # Temporarily removed
def get_manage_data(): # Changed function name
    """
    API endpoint che restituisce tutti gli account e le app per la pagina di gestione, come JSON.
    """
    all_accounts = get_all_accounts()
    all_apps = get_all_apps()
    # logged_in_user = get_user_by_id(session['user_id']) # Removed session usage
    return jsonify({'accounts': all_accounts, 'apps': all_apps}) # Return JSON

@app.route('/api/accounts/add', methods=['POST']) # Changed route
# @login_required # Temporarily removed
def add_account_api(): # Changed function name
    """
    API endpoint per aggiungere un'associazione tra un'app e un account.
    """
    data = request.get_json()
    app_id = data.get('app_id')
    account_id = data.get('account_id')

    if not app_id or not account_id:
        return jsonify({'message': 'Missing app_id or account_id'}, 400)

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT OR IGNORE INTO app_accounts (app_id, account_id) VALUES (?, ?)',
            (app_id, account_id)
        )
        conn.commit()
        return jsonify({'message': 'Association added successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error adding association: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/accounts/remove', methods=['POST']) # Changed route
# @login_required # Temporarily removed
def remove_account_api(): # Changed function name
    """
    API endpoint per rimuovere un'associazione tra un'app e un account.
    """
    data = request.get_json()
    app_id = data.get('app_id')
    account_id = data.get('account_id')

    if not app_id or not account_id:
        return jsonify({'message': 'Missing app_id or account_id'}, 400)

    conn = get_db_connection()
    try:
        conn.execute(
            'DELETE FROM app_accounts WHERE app_id = ? AND account_id = ?',
            (app_id, account_id)
        )
        conn.commit()
        return jsonify({'message': 'Association removed successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error removing association: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/accounts', methods=['POST']) # Changed route
# @login_required # Temporarily removed
def add_new_account_api(): # Changed function name
    """
    API endpoint per aggiungere un nuovo account.
    """
    data = request.get_json()
    name = data.get('name')
    abbreviation = data.get('abbreviation')

    if not name:
        return jsonify({'message': 'Missing account name'}, 400)

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO accounts (name, abbreviation) VALUES (?, ?)',
            (name, abbreviation)
        )
        conn.commit()
        return jsonify({'message': 'Account added successfully', 'id': cursor.lastrowid})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'An account with this name already exists'}, 409) # 409 Conflict
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error adding account: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/accounts/<int:account_id>', methods=['DELETE']) # Changed route
# @login_required # Temporarily removed
def delete_account_api(account_id): # Changed function name
    """
    API endpoint per eliminare un account e tutte le sue associazioni.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM app_accounts WHERE account_id = ?', (account_id,))
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        conn.commit()
        return jsonify({'message': f'Account ID {account_id} deleted successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error deleting account: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/accounts/<int:account_id>', methods=['PUT']) # Changed route
# @login_required # Temporarily removed
def update_account_settings_api(account_id): # Changed function name
    """
    API endpoint per aggiornare le impostazioni (ordine, visibilità) di un account.
    """
    data = request.get_json()
    order = data.get('order', type=int)
    is_hidden = 1 if data.get('is_hidden') else 0 # From boolean in JSON

    if account_id is None:
        return jsonify({'message': 'Missing account_id'}, 400)

    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE accounts SET "order" = ?, is_hidden = ? WHERE id = ?',
            (order, is_hidden, account_id)
        )
        conn.commit()
        return jsonify({'message': f'Account ID {account_id} settings updated successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error updating account settings: {e}'}, 500)
    finally:
        conn.close()
            
@app.route('/api/apps', methods=['POST']) # Changed route
# @login_required # Temporarily removed
def add_new_app_api(): # Changed function name
    """
    API endpoint per aggiungere una nuova applicazione.
    """
    data = request.get_json()
    name = data.get('name')
    folder = data.get('folder')

    if not name or not folder:
        return jsonify({'message': 'Missing app name or folder'}, 400)

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO apps (name, folder) VALUES (?, ?)',
            (name, folder)
        )
        conn.commit()
        return jsonify({'message': 'App added successfully', 'id': cursor.lastrowid})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'An app with this name already exists'}, 409) # 409 Conflict
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error adding app: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/apps/<int:app_id>', methods=['DELETE']) # Changed route
# @login_required # Temporarily removed
def delete_app_api(app_id): # Changed function name
    """
    API endpoint per eliminare un'applicazione e tutte le sue associazioni.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM app_accounts WHERE app_id = ?', (app_id,))
        cursor.execute('DELETE FROM apps WHERE id = ?', (app_id,))
        conn.commit()
        return jsonify({'message': f'App ID {app_id} deleted successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error deleting app: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/apps/<int:app_id>', methods=['PUT']) # Changed route
# @login_required # Temporarily removed
def update_app_settings_api(app_id): # Changed function name
    """
    API endpoint per aggiornare le impostazioni (ordine, visibilità) di un'applicazione.
    """
    data = request.get_json()
    order = data.get('order', type=int)
    is_hidden = 1 if data.get('is_hidden') else 0

    if app_id is None:
        return jsonify({'message': 'Missing app_id'}, 400)

    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE apps SET "order" = ?, is_hidden = ? WHERE id = ?',
            (order, is_hidden, app_id)
        )
        conn.commit()
        return jsonify({'message': f'App ID {app_id} settings updated successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message': f'Error updating app settings: {e}'}, 500)
    finally:
        conn.close()

@app.route('/api/login', methods=['POST']) # Changed route
def login_api(): # Changed function name
    """
    API endpoint per gestire il login utente.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = get_user_by_username(username)

    if user and check_password_hash(user['password_hash'], password):
        # For now, return a placeholder token. JWT implementation will replace this.
        # This will be replaced by a proper JWT token later
        placeholder_token = "your_placeholder_jwt_token_here" 
        return jsonify({'message': 'Login successful', 'token': placeholder_token, 'user_id': user['id'], 'username': user['username']})
    else:
        return jsonify({'message': 'Invalid credentials'}, 401)

@app.route('/api/logout', methods=['POST']) # Changed route
# @login_required # Temporarily removed
def logout_api(): # Changed function name
    """
    API endpoint per gestire il logout utente.
    """
    # For token-based auth, logout is often handled client-side by deleting the token.
    # This endpoint can be used for server-side token invalidation or just a confirmation.
    # session.pop('user_id', None) # Session-based logout is removed
    return jsonify({'message': 'Logout successful'})

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_mode)
