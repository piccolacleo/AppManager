# Manuale di Deployment Online con Render

Questo manuale ti guida passo dopo passo nella pubblicazione della tua applicazione "Gestione Account App" su Internet. Utilizzeremo un servizio chiamato [Render](https://render.com/), che offre un piano gratuito ideale per piccoli progetti come questo.

L'idea è semplice: caricherai il tuo codice su GitHub (un servizio per ospitare codice) e Render automaticamente lo prenderà da lì, lo installerà e lo renderà accessibile tramite un link pubblico (es. `https://nome-che-scegli.onrender.com`).

---

### Prerequisito Fondamentale: Account GitHub

Se non ne hai già uno, crea un account gratuito su [GitHub](https://github.com/). GitHub sarà la "casa" del tuo codice sorgente.

---

### Passo 1: Prepara e Carica il tuo Codice

1.  **Crea un Repository su GitHub:**
    *   Vai su GitHub e clicca su "Create a new repository".
    *   Dagli un nome (es. `gestione-app`), assicurati che sia "Public" e clicca su "Create repository".

2.  **Carica i File del Progetto:**
    *   Nella pagina del repository appena creato, clicca su "Add file" -> "Upload files".
    *   Trascina **tutti i file e le cartelle** del tuo progetto (`Dati`, `Script`, `UI`, `README.md`, `requirements.txt`, etc.) nella finestra del browser.
    *   Attendi il caricamento e poi clicca su "Commit changes".

    > **Nota:** Assicurati di non caricare il database `gestione.db` se contiene dati sensibili. Il nostro script lo creerà online.

---

### Passo 2: Crea e Configura il Servizio su Render

1.  **Crea un Account su Render:**
    *   Vai su [render.com](https://render.com/) e registrati (puoi usare direttamente il tuo account GitHub per fare prima).

2.  **Crea un Nuovo Servizio Web:**
    *   Dalla tua dashboard di Render, clicca su **New +** e seleziona **Web Service**.
    *   Se richiesto, collega il tuo account GitHub a Render.
    *   Trova il repository che hai creato prima (es. `gestione-app`) e clicca su **Connect**.

3.  **Configura le Impostazioni del Servizio:**
    Render ti chiederà alcune informazioni per capire come eseguire il tuo progetto. Compila i campi in questo modo:

    *   **Name:** Scegli un nome unico per il tuo sito (es. `gestione-app-personale`). L'URL sarà `https://NOME-SCELTO.onrender.com`.
    *   **Region:** Lascia `Oregon (US West)` o scegli `Frankfurt (EU Central)` per essere più vicino all'Europa.
    *   **Branch:** Lascia `main` (o il nome del tuo branch principale).
    *   **Root Directory:** Lascia vuoto.
    *   **Runtime:** Seleziona `Python 3`.
    *   **Build Command:** In questo campo, copia e incolla la riga seguente. Questo comando installerà le librerie necessarie e creerà il database la prima volta.
        ```bash
        pip install -r requirements.txt && python Dati/import_data.py
        ```
    *   **Start Command:** In questo campo, copia e incolla la riga seguente. Questo comando avvia l'applicazione web.
        ```bash
        gunicorn 'Script.app:app'
        ```
    *   **Instance Type:** Seleziona `Free`.

4.  **Avvia il Deployment:**
    *   Scorri fino in fondo alla pagina e clicca sul pulsante **Create Web Service**.

---

### Passo 3: Attendi e Vai Online!

Render inizierà ora il processo di "deployment":
- Installerà le dipendenze (`pip install...`).
- Eseguirà il build command (creando il database con `import_data.py`).
- Avvierà il server (`gunicorn...`).

Puoi seguire l'avanzamento nella sezione "Logs" o "Events". La prima volta potrebbe richiedere alcuni minuti.

Quando vedi il messaggio **"Your service is live"**, significa che ha finito!
In cima alla pagina, troverai l'URL pubblico della tua applicazione (es. `https://gestione-app-personale.onrender.com`).

**Cliccaci sopra e la tua applicazione sarà online, accessibile da qualsiasi PC o cellulare!**

---

### Aggiornamenti Futuri

La parte migliore di questo sistema è che, da ora in poi, ogni volta che caricherai una modifica su GitHub (sul branch `main`), Render automaticamente aggiornerà l'applicazione online per te.
