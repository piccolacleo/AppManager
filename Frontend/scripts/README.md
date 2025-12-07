# Gestione Account App - Manuale di Sviluppo AI

Questo documento serve come guida completa per lo sviluppo, la manutenzione e l'evoluzione dell'applicazione "Gestione Account App". È stato progettato per essere interpretato da un'intelligenza artificiale sviluppatrice, garantendo che chiunque possa comprendere e modificare il software in modo coerente.

**L'utente finale non deve mai modificare direttamente il codice.** Tutte le modifiche e le nuove funzionalità verranno implementate dall'IA sulla base dei feedback forniti dall'utente.

## 1. Obiettivo dell'Applicazione

L'applicazione è un mini-gestionale web che permette all'utente di tracciare la relazione tra le applicazioni installate su un dispositivo e gli account (utenze) ad esse associate.

Le funzionalità principali sono:
- Visualizzare un elenco di tutte le app, raggruppate per cartella e ordinate alfabeticamente.
- Associare uno o più account a ciascuna app.
- Rimuovere l'associazione tra un'app e un account.
- L'interfaccia deve essere semplice, pulita e accessibile sia da PC che da dispositivi mobili tramite browser web.

## 2. Stack Tecnologico

- **Linguaggio:** Python
- **Framework Web:** Flask
- **Database:** SQLite
- **Lettura Dati Iniziali:** Pandas & openpyxl
- **Frontend:** HTML con Jinja2 e CSS

## 3. Struttura del Progetto

Il progetto segue una struttura di cartelle personalizzata per separare logica, dati e interfaccia.

```
/AppManager/
|-- Dati/
|   |-- AppCell.xlsx      # File Excel originale con i dati
|   |-- gestione.db       # Database SQLite
|   |-- database.py       # Script per la creazione dello schema del DB
|   |-- import_data.py    # Script per l'importazione dei dati da Excel
|   |-- inspector.py      # Script di utility per ispezionare il file Excel
|
|-- Script/
|   |-- app.py            # Cuore dell'applicazione Flask (backend)
|
|-- UI/
|   |-- index.html        # Template HTML per l'interfaccia
|   |-- style.css         # Foglio di stile
|
|-- README.md             # Questo file, la documentazione centrale
|-- requirements.txt      # Dipendenze Python
```

## 4. Checklist di Sviluppo

Questa checklist traccia lo stato di avanzamento del progetto.

### Fase 1: Setup e Prodotto Minimo Funzionante (MVP) - COMPLETATA
- [x] **1.1.** Creare la struttura di cartelle e file.
- [x] **1.2.** Creare `requirements.txt` con le dipendenze.
- [x] **1.3.** **Database:** In `Dati/database.py`, definire lo schema del DB.
- [x] **1.4.** **Import Dati:** In `Dati/import_data.py`, implementare la logica di importazione.
- [x] **1.5.** **Backend:** In `Script/app.py`, creare l'applicazione Flask, le query e la logica di raggruppamento.
- [x] **1.6.** **Frontend:** In `UI/index.html`, creare la struttura per visualizzare i dati raggruppati.

### Fase 2: Funzionalità Interattive - COMPLETATA
- [x] **2.1.** **Aggiungi Account:**
    - [x] In `UI/index.html`, per ogni app, aggiungere un form con un menu a discesa (`<select>`) contenente tutti gli account possibili e un pulsante "Aggiungi".
    - [x] In `Script/app.py`, creare una nuova rotta (`/add_account`) per gestire l'aggiunta.
- [x] **2.2.** **Rimuovi Account:**
    - [x] In `UI/index.html`, aggiungere un pulsante "Rimuovi" accanto a ogni account associato.
    - [x] In `Script/app.py`, creare una rotta (`/remove_account`) per gestire la rimozione.

### Fase 3: Miglioramenti e Funzionalità Future - COMPLETATA
- [x] **3.1.** **Styling:** Migliorare `UI/style.css` per rendere l'interfaccia più pulita e responsiva.
- [x] **3.2.** **Ricerca/Filtro:** Aggiungere una barra di ricerca per filtrare le app.
- [x] **3.3.** **Gestione App/Account:** Aggiungere funzionalità per creare/modificare app e account dall'interfaccia - COMPLETATA.
- [x] **3.4.** **Deployment Online:** Documentare i passaggi per la pubblicazione online. (Vedi `MANUALE_DEPLOYMENT.md`)
- [x] **3.5.** **Controllo avanzato di ordinamento e visibilità:** Implementare la possibilità di definire un ordinamento personalizzato e nascondere voci per account e applicazioni - COMPLETATA.

### Fase 4: Autenticazione Locale - COMPLETATA
- [x] **4.1.** **Database:** Aggiungere tabella `users` in `Dati/database.py`.
- [x] **4.2.** **Dependencies:** Aggiungere `Werkzeug` a `requirements.txt`.
- [x] **4.3.** **Admin Setup:** Creare `setup_admin.py` per l'utente `piccolacleo`.
- [x] **4.4.** **Backend:** Implementare login/logout e `login_required` in `Script/app.py`.
- [x] **4.5.** **Frontend:** Creare `UI/login.html` e aggiornare `UI/index.html` / `UI/manage.html`.
- [x] **4.6.** **Styling:** Aggiungere stili per `UI/login.html` in `UI/style.css`.

## 5. Manuale Operativo per l'IA

### Setup Iniziale
1.  **Imposta la Chiave Segreta:** Prima di avviare l'applicazione, imposta una chiave segreta per Flask. È fondamentale per la sicurezza delle sessioni.
    *   **Windows (PowerShell):** `$env:FLASK_SECRET_KEY = "la_tua_chiave_segreta_lunga_e_complessa"`
    *   **Linux/macOS:** `export FLASK_SECRET_KEY="la_tua_chiave_segreta_lunga_e_complessa"`
    *   **Importante:** Scegli una chiave molto lunga e difficile da indovinare per la produzione.
2.  Esegui `pip install -r requirements.txt` per installare le dipendenze.
3.  Esegui `python Dati/import_data.py` (dalla cartella `AppManager`) per creare e popolare `gestione.db`.
4.  **Crea Utente Amministratore:** Esegui `python setup_admin.py` (dalla cartella `AppManager`) per creare l'utente `piccolacleo` e impostare la sua password. Questo script va eseguito solo la prima volta o se si vuole resettare la password dell'amministratore (dopo aver cancellato il database).
5.  Esegui `flask --app Script/app run` (dalla cartella `AppManager`) per avviare il server.
6.  Apri il browser all'indirizzo `http://127.0.0.1:5000`. Sarai reindirizzato alla pagina di login.

### Ciclo di Sviluppo (basato su feedback utente)
1.  **Analizza il feedback.**
2.  **Identifica i file da modificare:**
    - Logica di business, rotte -> `Script/app.py`
    - Struttura del database, query -> `Dati/database.py`
    - Script di setup/amministrazione -> `setup_admin.py`
    - Struttura e layout della pagina -> `UI/index.html`, `UI/manage.html`, `UI/login.html`
    - Stile (colori, font, dimensioni) -> `UI/style.css`
3.  **Implementa la modifica.**
4.  **Verifica:** Riavvia l'applicazione e controlla il risultato.
5.  **Aggiorna la documentazione:** Aggiorna questa checklist.

Questo documento è la fonte di verità del progetto. Mantenerlo aggiornato è un task prioritario.
