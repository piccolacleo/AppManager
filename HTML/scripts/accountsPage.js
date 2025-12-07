// scripts/accountsPage.js

document.addEventListener('DOMContentLoaded', () => {
    const accountsListBody = document.getElementById('accounts-list-body');
    const appsListBody = document.getElementById('apps-list-body');
    const addAccountForm = document.getElementById('add-account-form');
    const addAppForm = document.getElementById('add-app-form');

    // Funzione per rendere un elemento di testo editabile inline
    function makeEditable(element, id, field, manager) {
        element.addEventListener('click', () => {
            const originalValue = element.textContent;
            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalValue;
            input.className = 'editable-input'; // Aggiungi una classe per lo styling, se necessario

            // Sostituisci il testo con l'input
            element.replaceWith(input);
            input.focus();

            // Funzione per salvare le modifiche
            const saveChanges = () => {
                const newValue = input.value.trim();
                if (newValue !== originalValue) {
                    const updateObject = { id: id };
                    updateObject[field] = newValue;
                    if (manager === accountManager) {
                        manager.updateAccount(updateObject);
                    } else if (manager === appManager) {
                        manager.updateApp(updateObject);
                    }
                    // Rerender della tabella per riflettere le modifiche e ricreare gli handler
                    if (manager === accountManager) renderAccounts();
                    else if (manager === appManager) renderApps();
                } else {
                    input.replaceWith(element); // Torna all'elemento originale se nessun cambiamento
                }
            };

            // Salva al blur (perdita di focus)
            input.addEventListener('blur', saveChanges);

            // Salva alla pressione di Enter
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    input.blur(); // Triggera l'evento blur per salvare
                }
            });
        });
    }

    // Funzione per renderizzare gli account
    function renderAccounts() {
        accountsListBody.innerHTML = ''; // Pulisci il tbody
        const accounts = accountManager.getAccounts().sort((a, b) => a.order - b.order);

        accounts.forEach(account => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-account-id', account.id);
            tr.innerHTML = `
                <td data-label="Nome"><span class="editable-text" data-field="name">${account.name}</span></td>
                <td data-label="Abbreviazione"><span class="editable-text" data-field="abbreviation">${account.abbreviation || ''}</span></td>
                <td data-label="Ordine">
                    <form class="update-account-settings-form">
                        <input type="hidden" name="id" value="${account.id}">
                        <input type="number" name="order" value="${account.order}" class="order-input">
                    </form>
                </td>
                <td data-label="Nascosto">
                    <form class="update-account-settings-form">
                        <input type="hidden" name="id" value="${account.id}">
                        <input type="checkbox" name="is_hidden" ${account.isHidden ? 'checked' : ''}>
                    </form>
                </td>
                <td data-label="Azione">
                    <form class="delete-account-form">
                        <input type="hidden" name="id" value="${account.id}">
                        <button type="submit" class="remove-button">Elimina</button>
                    </form>
                </td>
            `;
            accountsListBody.appendChild(tr);

            // Rendi i campi nome e abbreviazione editabili
            const nameSpan = tr.querySelector('[data-field="name"]');
            makeEditable(nameSpan, account.id, 'name', accountManager);
            const abbrSpan = tr.querySelector('[data-field="abbreviation"]');
            makeEditable(abbrSpan, account.id, 'abbreviation', accountManager);
        });

        attachAccountEventListeners();
    }

    // Funzione per renderizzare le app
    function renderApps() {
        appsListBody.innerHTML = ''; // Pulisci il tbody
        const apps = appManager.getApps().sort((a, b) => a.order - b.order);

        apps.forEach(app => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-app-id', app.id);
            tr.innerHTML = `
                <td data-label="Nome"><span class="editable-text" data-field="name">${app.name}</span></td>
                <td data-label="Cartella"><span class="editable-text" data-field="folder">${app.folder}</span></td>
                <td data-label="Ordine">
                    <form class="update-app-settings-form">
                        <input type="hidden" name="id" value="${app.id}">
                        <input type="number" name="order" value="${app.order}" class="order-input">
                    </form>
                </td>
                <td data-label="Nascosta">
                    <form class="update-app-settings-form">
                        <input type="hidden" name="id" value="${app.id}">
                        <input type="checkbox" name="is_hidden" ${app.isHidden ? 'checked' : ''}>
                    </form>
                </td>
                <td data-label="Azione">
                    <form class="delete-app-form">
                        <input type="hidden" name="id" value="${app.id}">
                        <button type="submit" class="remove-button">Elimina</button>
                    </form>
                </td>
            `;
            appsListBody.appendChild(tr);

            // Rendi i campi nome e cartella editabili
            const nameSpan = tr.querySelector('[data-field="name"]');
            makeEditable(nameSpan, app.id, 'name', appManager);
            const folderSpan = tr.querySelector('[data-field="folder"]');
            makeEditable(folderSpan, app.id, 'folder', appManager);
        });

        attachAppEventListeners();
    }

    // Funzioni per allegare gli event listener degli account
    function attachAccountEventListeners() {
        // Modifica ordine/visibilità account
        document.querySelectorAll('.update-account-settings-form').forEach(form => {
            form.onchange = () => {
                const id = form.querySelector('input[name="id"]').value;
                const order = form.querySelector('input[name="order"]') ? parseInt(form.querySelector('input[name="order"]').value) : undefined;
                const isHidden = form.querySelector('input[name="is_hidden"]') ? form.querySelector('input[name="is_hidden"]').checked : undefined;
                
                accountManager.updateAccount({ id, order, isHidden });
                renderAccounts(); // Rerender dopo la modifica
            };
        });

        // Elimina account
        document.querySelectorAll('.delete-account-form').forEach(form => {
            form.onsubmit = (event) => {
                event.preventDefault();
                const id = form.querySelector('input[name="id"]').value;
                if (confirm('Sei sicuro di voler eliminare questo account? Se è associato ad app, l\'eliminazione verrà bloccata.')) {
                    const deleted = accountManager.deleteAccount(id);
                    if (!deleted) {
                        alert('Impossibile eliminare l\'account. È ancora associato ad una o più app.');
                    }
                    renderAccounts(); // Rerender dopo la modifica
                }
            };
        });
    }

    // Funzioni per allegare gli event listener delle app
    function attachAppEventListeners() {
        // Modifica ordine/visibilità app
        document.querySelectorAll('.update-app-settings-form').forEach(form => {
            form.onchange = () => {
                const id = form.querySelector('input[name="id"]').value;
                const order = form.querySelector('input[name="order"]') ? parseInt(form.querySelector('input[name="order"]').value) : undefined;
                const isHidden = form.querySelector('input[name="is_hidden"]') ? form.querySelector('input[name="is_hidden"]').checked : undefined;
                
                appManager.updateApp({ id, order, isHidden });
                renderApps(); // Rerender dopo la modifica
            };
        });

        // Elimina app
        document.querySelectorAll('.delete-app-form').forEach(form => {
            form.onsubmit = (event) => {
                event.preventDefault();
                const id = form.querySelector('input[name="id"]').value;
                if (confirm('Sei sicuro di voler eliminare questa applicazione? Verranno rimosse tutte le sue associazioni.')) {
                    // Controlla se l\'app ha account associati prima di eliminare
                    const app = appManager.getAppById(id);
                    if (app && app.associatedAccounts.length > 0) {
                        alert('Impossibile eliminare l\'app. Ha account associati. Rimuovi prima le associazioni tramite la pagina "Gestione Account App".');
                    } else {
                        appManager.deleteApp(id);
                    }
                    renderApps(); // Rerender dopo la modifica
                }
            };
        });
    }

    // Aggiungi nuovo account
    addAccountForm.onsubmit = (event) => {
        event.preventDefault();
        const name = addAccountForm.querySelector('input[name="accountName"]').value;
        const abbreviation = addAccountForm.querySelector('input[name="accountAbbreviation"]').value;
        if (name) {
            accountManager.addAccount(name, abbreviation);
            addAccountForm.reset();
            renderAccounts();
        } else {
            alert('Il nome dell\'account è obbligatorio.');
        }
    };

    // Aggiungi nuova app
    addAppForm.onsubmit = (event) => {
        event.preventDefault();
        const name = addAppForm.querySelector('input[name="appName"]').value;
        const folder = addAppForm.querySelector('input[name="appFolder"]').value;
        if (name && folder) {
            appManager.addApp(name, folder);
            addAppForm.reset();
            renderApps();
        } else {
            alert('Il nome e la cartella dell\'applicazione sono obbligatori.');
        }
    };

    // Carica e renderizza al primo caricamento della pagina
    renderAccounts();
    renderApps();
});