// scripts/dataManager.js

// Funzione per generare un UUID v4
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Chiavi per localStorage
const LOCAL_STORAGE_KEYS = {
    APPS: 'appManager_apps',
    ACCOUNTS: 'appManager_accounts'
};

// Dati iniziali di esempio (se localStorage è vuoto)
const initialApps = (() => {
    const apps = [];
    const id1 = generateUUID();
    const id2 = generateUUID();
    const id3 = generateUUID();
    const id4 = generateUUID();
    const id5 = generateUUID();
    const id6 = generateUUID();
    const id7 = generateUUID();
    const id8 = generateUUID();

    apps.push({ id: id1, name: 'Gmail', folder: 'Google', order: 1, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id2, name: 'Google Calendar', folder: 'Google', order: 2, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id3, name: 'WhatsApp', folder: 'Social', order: 1, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id4, name: 'Telegram', folder: 'Social', order: 2, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id5, name: 'Outlook', folder: 'Microsoft', order: 1, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id6, name: 'Teams', folder: 'Microsoft', order: 2, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id7, name: 'Slack', folder: 'Business', order: 1, isHidden: false, associatedAccounts: [] });
    apps.push({ id: id8, name: 'Jira', folder: 'Business', order: 2, isHidden: false, associatedAccounts: [] });

    // Associa un account a un'app di esempio per test
    const userMainId = generateUUID(); // Genera un ID per user.main@example.com
    const userWorkId = generateUUID(); // Genera un ID per user.work@example.com

    apps[0].associatedAccounts.push(userMainId); // Gmail associato a user.main
    apps[2].associatedAccounts.push(userMainId); // WhatsApp associato a user.main
    apps[4].associatedAccounts.push(userWorkId); // Outlook associato a user.work

    // Aggiungi gli ID generati agli initialAccounts per garantire la coerenza
    initialAccounts[0].id = userMainId;
    initialAccounts[1].id = userWorkId;

    return apps;
})();

const initialAccounts = [
    { id: initialAccounts[0].id, name: 'user.main@example.com', abbreviation: 'UM', order: 1, isHidden: false },
    { id: initialAccounts[1].id, name: 'user.work@example.com', abbreviation: 'UW', order: 2, isHidden: false },
    { id: generateUUID(), name: 'admin@example.com', abbreviation: 'AD', order: 3, isHidden: false }
];

// Funzione per caricare i dati da localStorage
function loadData() {
    let apps = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEYS.APPS));
    let accounts = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEYS.ACCOUNTS));

    if (!apps || apps.length === 0) {
        apps = initialApps;
        saveData(apps, LOCAL_STORAGE_KEYS.APPS);
    }
    if (!accounts || accounts.length === 0) {
        accounts = initialAccounts;
        saveData(accounts, LOCAL_STORAGE_KEYS.ACCOUNTS);
    }

    // Assicurarsi che ogni app abbia un campo associatedAccounts valido
    apps.forEach(app => {
        if (!Array.isArray(app.associatedAccounts)) {
            app.associatedAccounts = [];
        }
    });
    saveData(apps, LOCAL_STORAGE_KEYS.APPS); // Salva per aggiornare eventuali campi mancanti

    return { apps, accounts };
}

// Funzione per salvare i dati in localStorage
function saveData(data, key) {
    localStorage.setItem(key, JSON.stringify(data));
}

// Funzioni per la gestione delle Apps
const appManager = {
    getApps: function() {
        return loadData().apps;
    },
    getAppById: function(id) {
        return this.getApps().find(app => app.id === id);
    },
    addApp: function(name, folder) {
        const apps = this.getApps();
        const newApp = {
            id: generateUUID(),
            name: name,
            folder: folder,
            order: apps.length > 0 ? Math.max(...apps.map(a => a.order)) + 1 : 1,
            isHidden: false,
            associatedAccounts: []
        };
        apps.push(newApp);
        saveData(apps, LOCAL_STORAGE_KEYS.APPS);
        return newApp;
    },
    updateApp: function(updatedApp) {
        let apps = this.getApps();
        const index = apps.findIndex(app => app.id === updatedApp.id);
        if (index !== -1) {
            apps[index] = { ...apps[index], ...updatedApp };
            saveData(apps, LOCAL_STORAGE_KEYS.APPS);
            return apps[index];
        }
        return null;
    },
    deleteApp: function(id) {
        let apps = this.getApps();
        const initialLength = apps.length;
        apps = apps.filter(app => app.id !== id);
        saveData(apps, LOCAL_STORAGE_KEYS.APPS);
        return apps.length < initialLength; // Ritorna true se un'app è stata cancellata
    },
    associateAccountToApp: function(appId, accountId) {
        const apps = this.getApps();
        const app = apps.find(a => a.id === appId);
        if (app && !app.associatedAccounts.includes(accountId)) {
            app.associatedAccounts.push(accountId);
            saveData(apps, LOCAL_STORAGE_KEYS.APPS);
            return true;
        }
        return false;
    },
    removeAccountFromApp: function(appId, accountId) {
        const apps = this.getApps();
        const app = apps.find(a => a.id === appId);
        if (app) {
            const initialLength = app.associatedAccounts.length;
            app.associatedAccounts = app.associatedAccounts.filter(accId => accId !== accountId);
            saveData(apps, LOCAL_STORAGE_KEYS.APPS);
            return app.associatedAccounts.length < initialLength; // Ritorna true se rimosso
        }
        return false;
    },
    getAccountsAssociatedWithApp: function(appId) {
        const app = this.getAppById(appId);
        if (!app) return [];
        const allAccounts = accountManager.getAccounts();
        return allAccounts.filter(account => app.associatedAccounts.includes(account.id));
    }
};

// Funzioni per la gestione degli Accounts
const accountManager = {
    getAccounts: function() {
        return loadData().accounts;
    },
    getAccountById: function(id) {
        return this.getAccounts().find(account => account.id === id);
    },
    addAccount: function(name, abbreviation) {
        const accounts = this.getAccounts();
        const newAccount = {
            id: generateUUID(),
            name: name,
            abbreviation: abbreviation,
            order: accounts.length > 0 ? Math.max(...accounts.map(a => a.order)) + 1 : 1,
            isHidden: false
        };
        accounts.push(newAccount);
        saveData(accounts, LOCAL_STORAGE_KEYS.ACCOUNTS);
        return newAccount;
    },
    updateAccount: function(updatedAccount) {
        let accounts = this.getAccounts();
        const index = accounts.findIndex(account => account.id === updatedAccount.id);
        if (index !== -1) {
            accounts[index] = { ...accounts[index], ...updatedAccount };
            saveData(accounts, LOCAL_STORAGE_KEYS.ACCOUNTS);
            return accounts[index];
        }
        return null;
    },
    deleteAccount: function(id) {
        // Prima di eliminare, controllare se l'account è associato a qualsiasi app
        const apps = appManager.getApps();
        const isAssociated = apps.some(app => app.associatedAccounts.includes(id));
        if (isAssociated) {
            console.warn(`L'account con ID ${id} è associato ad alcune app. Impossibile eliminare.`);
            return false; // Non eliminare se associato
        }

        let accounts = this.getAccounts();
        const initialLength = accounts.length;
        accounts = accounts.filter(account => account.id !== id);
        saveData(accounts, LOCAL_STORAGE_KEYS.ACCOUNTS);
        return accounts.length < initialLength; // Ritorna true se un account è stato cancellato
    }
};

// Inizializza i dati all'avvio
document.addEventListener('DOMContentLoaded', loadData);
