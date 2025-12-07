import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Creazione dell'applicazione Flask con percorsi personalizzati per UI e static
app = Flask(__name__, template_folder='../', static_folder='../utility') # Templates in root, static in utility

# Configurazione della chiave segreta per le sessioni
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24)) # Usa una chiave sicura per le sessioni

# Flag per controllare se il login è abilitato
LOGIN_ENABLED = os.environ.get('LOGIN_ENABLED', '0') == '1'
# print(f"LOGIN_ENABLED is set to: {LOGIN_ENABLED}") # For debugging

# Definisce il percorso del database nella cartella Dati/mdb-database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '../Dati/mdb-database/gestione.db')

def get_db_connection():
    """Crea una connessione al database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_id(user_id):
    """Recupera un utente dal database tramite ID."""
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    """Recupera un utente dal database tramite username."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def login_required(f):
    """Decoratore per proteggere le rotte che richiedono l'autenticazione, se abilitata."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not LOGIN_ENABLED:
            return f(*args, **kwargs) # Se login disabilitato, procedi
        
        if 'user_id' not in session:
            flash('Accedi per accedere a questa pagina.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        sorted_apps = sorted(apps.values(), key=lambda x: (x['order'], x['name']))
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
    all_accounts = get_all_accounts()
    logged_in_user = get_user_by_id(session.get('user_id')) if 'user_id' in session else None
    return render_template('index.html', apps_by_folder=apps_by_folder, all_accounts=all_accounts, logged_in_user=logged_in_user)

@app.route('/manage')
@login_required
def manage():
    """
    Pagina per la gestione di app e account. Richiede autenticazione (se abilitata).
    """
    all_accounts = get_all_accounts()
    all_apps = get_all_apps()
    logged_in_user = get_user_by_id(session['user_id']) if 'user_id' in session else None
    return render_template('manage.html', all_accounts=all_accounts, all_apps=all_apps, logged_in_user=logged_in_user)

@app.route('/add_account', methods=['POST'])
@login_required
def add_account():
    """
    Aggiunge un'associazione tra un'app e un account nel database. Richiede autenticazione (se abilitata).
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
        flash('Associazione aggiunta con successo.', 'success')

    return redirect(url_for('index'))

@app.route('/remove_account', methods=['POST'])
@login_required
def remove_account():
    """
    Rimuove un'associazione tra un'app e un account dal database. Richiede autenticazione (se abilitata).
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
        flash('Associazione rimossa con successo.', 'success')
    
    return redirect(url_for('index'))

@app.route('/add_new_account', methods=['POST'])
@login_required
def add_new_account():
    """
    Aggiunge un nuovo account al database. Richiede autenticazione (se abilitata).
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
            flash('Account aggiunto con successo.', 'success')
        except sqlite3.IntegrityError:
            flash('Un account con questo nome esiste già.', 'error')
        finally:
            conn.close()

    return redirect(url_for('manage'))

@app.route('/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    """
    Elimina un account e tutte le sue associazioni. Richiede autenticazione (se abilitata).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM app_accounts WHERE account_id = ?', (account_id,))
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        conn.commit()
        flash(f'Account ID {account_id} eliminato con successo.', 'success')
    except sqlite3.Error as e:
        print(f"Errore durante l'eliminazione dell'account: {e}")
        conn.rollback()
        flash('Errore durante l\'eliminazione dell\'account.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage'))

@app.route('/update_account_settings', methods=['POST'])
@login_required
def update_account_settings():
    """
    Aggiorna le impostazioni (ordine, visibilità) di un account. Richiede autenticazione (se abilitata).
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
            flash(f'Impostazioni account ID {account_id} aggiornate.', 'success')
        except sqlite3.Error as e:
            print(f"Errore durante l\'aggiornamento dell\'account: {e}")
            conn.rollback()
            flash('Errore durante l\'aggiornamento delle impostazioni account.', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('manage'))

@app.route('/add_new_app', methods=['POST'])
@login_required
def add_new_app():
    """
    Aggiunge una nuova applicazione al database. Richiede autenticazione (se abilitata).
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
            flash(f'Applicazione {name} aggiunta con successo.', 'success')
        except sqlite3.IntegrityError:
            flash('Un\'applicazione con questo nome esiste già.', 'error')
        finally:
            conn.close()

    return redirect(url_for('manage'))

@app.route('/delete_app/<int:app_id>', methods=['POST'])
@login_required
def delete_app(app_id):
    """
    Elimina un\'applicazione e tutte le sue associazioni. Richiede autenticazione (se abilitata).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM app_accounts WHERE app_id = ?', (app_id,))
        cursor.execute('DELETE FROM apps WHERE id = ?', (app_id,))
        conn.commit()
        flash(f'Applicazione ID {app_id} eliminata con successo.', 'success')
    except sqlite3.Error as e:
        print(f"Errore durante l\'eliminazione dell\'app: {e}")
        conn.rollback()
        flash('Errore durante l\'eliminazione dell\'applicazione.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage'))

@app.route('/update_app_settings', methods=['POST'])
@login_required
def update_app_settings():
    """
    Aggiorna le impostazioni (ordine, visibilità) di un\'applicazione. Richiede autenticazione (se abilitata).
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
            flash(f'Impostazioni applicazione ID {app_id} aggiornate.', 'success')
        except sqlite3.Error as e:
            print(f"Errore durante l\'aggiornamento dell\'app: {e}")
            conn.rollback()
            flash('Errore durante l\'aggiornamento delle impostazioni applicazione.', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('manage'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gestisce il login utente.
    """
    if not LOGIN_ENABLED:
        flash("Login disabilitato per configurazione.", "info")
        return redirect(url_for('index')) # Se login disabilitato, reindirizza alla home
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user_by_username(username)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Accesso effettuato con successo!', 'success')
            return redirect(url_for('manage')) # Reindirizza alla pagina di gestione dopo il login
        else:
            flash('Credenziali non valide. Riprova.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Gestisce il logout utente.
    """
    if not LOGIN_ENABLED:
        flash("Login disabilitato per configurazione.", "info")
        return redirect(url_for('index'))

    session.pop('user_id', None)
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Usa FLASK_DEBUG per controllare la modalità debug
    debug_mode = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_mode)
