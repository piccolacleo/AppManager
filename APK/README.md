
# App Gestione App e Utenze (Android + Windows)

## ✅ Funzionalità Implementate
- [x] Creazione database SQLite locale (`data.db`)
- [x] Tabelle: App, Utenze, Relazioni App-Utenze
- [x] Interfaccia Kivy per Android
- [x] Pulsanti per:
  - Aggiungi App (popup Nome + Descrizione)
  - Aggiungi Utenza (popup Indirizzo, Gruppo, Uso, Cliente, Ordine)
  - Lista App
  - Lista Utenze
  - Esporta DB (crea `exported_data.db`)

## 🔜 Da Fare
- [ ] Aggiungere pulsanti **Modifica** ed **Elimina** per App e Utenze
- [ ] Gestione relazioni App ↔ Utenze con popup di selezione
- [ ] Migliorare layout con `RecycleView` per liste interattive
- [ ] Creare versione Windows con interfaccia Tkinter/PyQt
- [ ] Compilare `.exe` per Windows con PyInstaller

---

## 📦 Come Compilare APK per Android

1. **Installa Kivy e Buildozer**:
   ```bash
   pip install kivy buildozer
   ```

2. **Crea il file `main.py`** (già fornito).

3. **Inizializza il progetto Buildozer**:
   ```bash
   buildozer init
   ```

4. **Modifica `buildozer.spec`**:
   - Imposta `source.dir = .`
   - Aggiungi permessi per accesso file:
     ```
     android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
     ```

5. **Compila l'APK**:
   ```bash
   buildozer android debug
   ```

6. **Trova l'APK** in `bin/` e installalo sul telefono.

---

## 📤 Come Esportare il DB
- Nell'app, premi **Esporta DB**.
- Il file `exported_data.db` sarà nella cartella dell'app.
- Puoi inviarlo via email o copiarlo su PC.

---

## 🖥 Versione Windows
- Usa lo stesso `data.db`.
- Crea interfaccia con Tkinter o PyQt.
- Compila in `.exe` con PyInstaller:
   ```bash
   pyinstaller --onefile main.py
   ```

---

## 🔍 Snippet di Codice Utili

### Creazione DB e Tabelle
```python
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS app (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, descrizione TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS utenze (id INTEGER PRIMARY KEY AUTOINCREMENT, indirizzo TEXT, gruppo TEXT, uso TEXT, cliente TEXT, ordine INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS app_utenze (id_app INTEGER, id_utenza INTEGER, PRIMARY KEY(id_app, id_utenza))")
conn.commit()
```

### Aggiunta App
```python
def aggiungi_app(nome, descrizione):
    cursor.execute("INSERT INTO app (nome, descrizione) VALUES (?, ?)", (nome, descrizione))
    conn.commit()
```

### Popup per Inserimento Dati (Kivy)
```python
layout = BoxLayout(orientation='vertical')
nome_input = TextInput(hint_text="Nome App")
descr_input = TextInput(hint_text="Descrizione")
btn_save = Button(text="Salva")
btn_save.bind(on_press=lambda x: salva(nome_input.text, descr_input.text))
```

---

## ✅ Compatibilità
- Il file `data.db` è condiviso tra Android e Windows.
