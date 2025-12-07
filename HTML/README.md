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

- implementa questa parte considerando che voglio delle pagine web subito accessibili via browser, caricate su un cloud (la sicurezza è data dall'accesso al cloud).
- ho immaginato pagine web visibili e gestibili da telefono e da pc. una interfaccia non scorrevole ma gestita a tab, menu compressi, con varie funzioni da sviluppare di volta in volta.
- l'applicazione sarà subito visibile dal file principale, la index.html ad esempio.

## 3. Struttura del Progetto

Il progetto segue una struttura di cartelle personalizzata per separare logica, dati e interfaccia.

```
/AppManager/HTML/
|-- mdb-database/
|   |-- gestione.db       # Database SQLite
|
|-- script/
|   |-- app.py            # Cuore dell'applicazione Flask (backend)
|	|-- requirements.txt  # Dipendenze Python
|	|-- setup_admin.py	  # non considerare per ora
|
|-- utility/
|   |-- style.css         # Foglio di stile
|
|-- README.md             # Questo file, la documentazione centrale
|-- index.html            # Template HTML per l'interfaccia # modifica il file esistente: sarà solo un contenitore per l'accesso alle varie funzionalità che in futuro potrebbero essere la gestione di file, appunti, progetti.
|-- apps.html             # Gestione App
|-- accounts.html         # Gestione Account
```

## 4. Checklist di Sviluppo

Crea checklist per tracciare lo stato di avanzamento del progetto.

- ** Modificare la pagina index.html`per mostrare le sezioni Apps e Accounts
- ** Modifica le pagine Apps e Accounts per mostrare una lista, la possibilità di Aggiuta, Modifica, Cancellazione dello stesso.
	*** Se account, possibilità di aggiungere, rimuovere app che usa.
	***	Posso cancellare l'account solo se non ho App associate.
	*** Se app possibilità di aggiungerci utenti, o rimuoverne.
	*** Posso cancellare l'app solo se non ho Account associati.
- ** Styling per migliorare l'interfaccia: deve essere più pulita e responsiva.
- ** Ricerca/Filtro: Aggiungere una barra di ricerca per filtrare le app.
- ** Controllo avanzato di ordinamento e visibilità: Implementare la possibilità di definire un ordinamento personalizzato e nascondere voci per account e applicazioni.


## 5. Manuale Operativo per l'IA

### Ciclo di Sviluppo (basato su feedback utente)
1.  **Analizza il feedback.**
2.  **Identifica i file da modificare:**
3.  **Implementa la modifica.**
4.  **Verifica:** implementa test e2e per verificare il corretto funzionamento richiesto
5.  **Aggiorna la documentazione:** Aggiorna questa checklist e file di documentazione.

Questo documento è la fonte di verità del progetto. Mantenerlo aggiornato è un task prioritario.
