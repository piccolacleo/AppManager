// scripts/appsPage.js

document.addEventListener('DOMContentLoaded', () => {
    const appListContainer = document.getElementById('app-list-container');
    const searchBar = document.getElementById('search-bar');
    const noAppsMessage = document.getElementById('no-apps-message');

    let allApps = [];
    let allAccounts = [];

    // Funzione per renderizzare tutte le app
    function renderApps(appsToRender) {
        appListContainer.innerHTML = ''; // Pulisci il contenitore

        if (appsToRender.length === 0) {
            noAppsMessage.style.display = 'block';
            return;
        } else {
            noAppsMessage.style.display = 'none';
        }

        // Raggruppa le app per cartella
        const appsByFolder = appsToRender.reduce((acc, app) => {
            if (!acc[app.folder]) {
                acc[app.folder] = [];
            }
            acc[app.folder].push(app);
            return acc;
        }, {});

        // Ordina le cartelle alfabeticamente
        const sortedFolders = Object.keys(appsByFolder).sort((a, b) => a.localeCompare(b));

        sortedFolders.forEach(folderName => {
            const folderSection = document.createElement('section');
            folderSection.className = 'folder-section';
            folderSection.setAttribute('data-folder', folderName);

            const folderTitle = document.createElement('h2');
            folderTitle.textContent = folderName;
            folderSection.appendChild(folderTitle);

            const table = document.createElement('table');
            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th>Applicazione</th>
                    <th>Account Associati</th>
                </tr>
            `;
            table.appendChild(thead);

            const tbody = document.createElement('tbody');

            // Ordina le app all'interno della cartella per nome o ordine
            const sortedAppsInFolder = appsByFolder[folderName].sort((a, b) => a.name.localeCompare(b.name));

            sortedAppsInFolder.forEach(app => {
                const tr = document.createElement('tr');
                tr.className = 'app-row';
                tr.setAttribute('data-app-id', app.id);

                const appNameTd = document.createElement('td');
                appNameTd.setAttribute('data-label', 'Applicazione');
                appNameTd.textContent = app.name;
                tr.appendChild(appNameTd);

                const accountsTd = document.createElement('td');
                accountsTd.setAttribute('data-label', 'Account Associati');

                const accountListUl = document.createElement('ul');
                accountListUl.className = 'account-list';

                const associatedAccounts = appManager.getAccountsAssociatedWithApp(app.id);

                if (associatedAccounts.length > 0) {
                    associatedAccounts.forEach(account => {
                        const li = document.createElement('li');
                        li.setAttribute('data-account-id', account.id);
                        li.innerHTML = `
                            <span>${account.name}</span>
                            <form class="remove-form">
                                <input type="hidden" name="app_id" value="${app.id}">
                                <input type="hidden" name="account_id" value="${account.id}">
                                <button type="submit" class="remove-button">Rimuovi</button>
                            </form>
                        `;
                        accountListUl.appendChild(li);
                    });
                } else {
                    const span = document.createElement('span');
                    span.className = 'no-accounts';
                    span.textContent = 'Nessun account associato';
                    accountListUl.appendChild(span);
                }

                accountsTd.appendChild(accountListUl);

                // Form per aggiungere un nuovo account
                const addAccountDiv = document.createElement('div');
                addAccountDiv.className = 'add-account-form';
                const addAccountForm = document.createElement('form');
                addAccountForm.innerHTML = `
                    <input type="hidden" name="app_id" value="${app.id}">
                    <select name="account_id" aria-label="Seleziona un account da aggiungere">
                        <option value="">Aggiungi account...</option>
                        ${allAccounts.sort((a, b) => a.name.localeCompare(b.name)).map(account => `
                            <option value="${account.id}">${account.name}</option>
                        `).join('')}
                    </select>
                    <button type="submit">Aggiungi</button>
                `;
                addAccountDiv.appendChild(addAccountForm);
                accountsTd.appendChild(addAccountDiv);

                tr.appendChild(accountsTd);
                tbody.appendChild(tr);
            });

            table.appendChild(tbody);
            folderSection.appendChild(table);
            appListContainer.appendChild(folderSection);
        });
        attachEventListeners(); // Allega gli event listener dopo il rendering
    }

    // Funzione per allegare gli event listener
    function attachEventListeners() {
        // Event listener per la rimozione di account
        document.querySelectorAll('.remove-form').forEach(form => {
            form.onsubmit = (event) => {
                event.preventDefault();
                const appId = form.querySelector('input[name="app_id"]').value;
                const accountId = form.querySelector('input[name="account_id"]').value;
                if (confirm('Sei sicuro di voler rimuovere questo account dall\'app?')) {
                    appManager.removeAccountFromApp(appId, accountId);
                    loadAndRender();
                }
            };
        });

        // Event listener per l'aggiunta di account
        document.querySelectorAll('.add-account-form form').forEach(form => {
            form.onsubmit = (event) => {
                event.preventDefault();
                const appId = form.querySelector('input[name="app_id"]').value;
                const accountId = form.querySelector('select[name="account_id"]').value;
                if (accountId) {
                    appManager.associateAccountToApp(appId, accountId);
                    loadAndRender();
                } else {
                    alert('Seleziona un account da aggiungere.');
                }
            };
        });
    }

    // Funzione principale per caricare e renderizzare i dati
    function loadAndRender() {
        const { apps, accounts } = loadData(); // Carica i dati usando la funzione di dataManager
        allApps = apps;
        allAccounts = accounts;

        // Filtra le app nascoste per la visualizzazione iniziale
        const visibleApps = allApps.filter(app => !app.isHidden);
        renderApps(visibleApps);
    }

    // Funzionalità di ricerca
    searchBar.addEventListener('input', () => {
        const searchTerm = searchBar.value.toLowerCase();
        const filteredApps = allApps.filter(app =>
            !app.isHidden && app.name.toLowerCase().includes(searchTerm)
        );
        renderApps(filteredApps);
    });

    // Carica e renderizza al primo caricamento della pagina
    loadAndRender();
});
