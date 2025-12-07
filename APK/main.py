
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import sqlite3
import os
import shutil

DB_FILE = "data.db"

# Creazione DB se non esiste
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS app (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descrizione TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS utenze (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indirizzo TEXT,
    gruppo TEXT,
    uso TEXT,
    cliente TEXT,
    ordine INTEGER
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS app_utenze (
    id_app INTEGER,
    id_utenza INTEGER,
    FOREIGN KEY(id_app) REFERENCES app(id),
    FOREIGN KEY(id_utenza) REFERENCES utenze(id),
    PRIMARY KEY(id_app, id_utenza)
);
""")
conn.commit()
conn.close()

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()

    # CRUD App
    def aggiungi_app(self, nome, descrizione):
        self.cursor.execute("INSERT INTO app (nome, descrizione) VALUES (?, ?)", (nome, descrizione))
        self.conn.commit()

    def modifica_app(self, id_app, nome, descrizione):
        self.cursor.execute("UPDATE app SET nome=?, descrizione=? WHERE id=?", (nome, descrizione, id_app))
        self.conn.commit()

    def elimina_app(self, id_app):
        self.cursor.execute("DELETE FROM app WHERE id=?", (id_app,))
        self.conn.commit()

    def lista_app(self):
        self.cursor.execute("SELECT * FROM app")
        return self.cursor.fetchall()

    # CRUD Utenze
    def aggiungi_utenza(self, indirizzo, gruppo, uso, cliente, ordine):
        self.cursor.execute("INSERT INTO utenze (indirizzo, gruppo, uso, cliente, ordine) VALUES (?, ?, ?, ?, ?)",
                            (indirizzo, gruppo, uso, cliente, ordine))
        self.conn.commit()

    def modifica_utenza(self, id_utenza, indirizzo, gruppo, uso, cliente, ordine):
        self.cursor.execute("UPDATE utenze SET indirizzo=?, gruppo=?, uso=?, cliente=?, ordine=? WHERE id=?",
                            (indirizzo, gruppo, uso, cliente, ordine, id_utenza))
        self.conn.commit()

    def elimina_utenza(self, id_utenza):
        self.cursor.execute("DELETE FROM utenze WHERE id=?", (id_utenza,))
        self.conn.commit()

    def lista_utenze(self):
        self.cursor.execute("SELECT * FROM utenze ORDER BY ordine")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.db = DBManager()

        self.add_widget(Label(text="Gestione App e Utenze"))

        # Pulsanti App
        btn_add_app = Button(text="Aggiungi App")
        btn_add_app.bind(on_press=self.add_app_popup)
        self.add_widget(btn_add_app)

        btn_edit_app = Button(text="Modifica App")
        btn_edit_app.bind(on_press=self.edit_app_popup)
        self.add_widget(btn_edit_app)

        btn_delete_app = Button(text="Elimina App")
        btn_delete_app.bind(on_press=self.delete_app_popup)
        self.add_widget(btn_delete_app)

        btn_list_app = Button(text="Lista App")
        btn_list_app.bind(on_press=self.show_apps)
        self.add_widget(btn_list_app)

        # Pulsanti Utenze
        btn_add_utenza = Button(text="Aggiungi Utenza")
        btn_add_utenza.bind(on_press=self.add_utenza_popup)
        self.add_widget(btn_add_utenza)

        btn_edit_utenza = Button(text="Modifica Utenza")
        btn_edit_utenza.bind(on_press=self.edit_utenza_popup)
        self.add_widget(btn_edit_utenza)

        btn_delete_utenza = Button(text="Elimina Utenza")
        btn_delete_utenza.bind(on_press=self.delete_utenza_popup)
        self.add_widget(btn_delete_utenza)

        btn_list_utenze = Button(text="Lista Utenze")
        btn_list_utenze.bind(on_press=self.show_utenze)
        self.add_widget(btn_list_utenze)

        # Pulsante esportazione DB
        btn_export = Button(text="Esporta DB")
        btn_export.bind(on_press=self.export_db)
        self.add_widget(btn_export)

    # Popup per aggiungere App
    def add_app_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        nome_input = TextInput(hint_text="Nome App")
        descr_input = TextInput(hint_text="Descrizione")
        layout.add_widget(nome_input)
        layout.add_widget(descr_input)
        btn_save = Button(text="Salva")

        def save_app(btn):
            self.db.aggiungi_app(nome_input.text, descr_input.text)
            popup.dismiss()

        btn_save.bind(on_press=save_app)
        layout.add_widget(btn_save)
        popup = Popup(title="Aggiungi App", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    # Popup per modificare App
    def edit_app_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        id_input = TextInput(hint_text="ID App")
        nome_input = TextInput(hint_text="Nuovo Nome")
        descr_input = TextInput(hint_text="Nuova Descrizione")
        for w in [id_input, nome_input, descr_input]:
            layout.add_widget(w)
        btn_save = Button(text="Modifica")

        def edit_app(btn):
            self.db.modifica_app(int(id_input.text), nome_input.text, descr_input.text)
            popup.dismiss()

        btn_save.bind(on_press=edit_app)
        layout.add_widget(btn_save)
        popup = Popup(title="Modifica App", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    # Popup per eliminare App
    def delete_app_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        id_input = TextInput(hint_text="ID App da eliminare")
        layout.add_widget(id_input)
        btn_delete = Button(text="Elimina")

        def delete_app(btn):
            self.db.elimina_app(int(id_input.text))
            popup.dismiss()

        btn_delete.bind(on_press=delete_app)
        layout.add_widget(btn_delete)
        popup = Popup(title="Elimina App", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    # Popup per aggiungere Utenza
    def add_utenza_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        indirizzo = TextInput(hint_text="Indirizzo")
        gruppo = TextInput(hint_text="Gruppo")
        uso = TextInput(hint_text="Uso")
        cliente = TextInput(hint_text="Cliente")
        ordine = TextInput(hint_text="Ordine (numero)")
        for w in [indirizzo, gruppo, uso, cliente, ordine]:
            layout.add_widget(w)
        btn_save = Button(text="Salva")

        def save_utenza(btn):
            self.db.aggiungi_utenza(indirizzo.text, gruppo.text, uso.text, cliente.text, int(ordine.text))
            popup.dismiss()

        btn_save.bind(on_press=save_utenza)
        layout.add_widget(btn_save)
        popup = Popup(title="Aggiungi Utenza", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    # Popup per modificare Utenza
    def edit_utenza_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        id_input = TextInput(hint_text="ID Utenza")
        indirizzo = TextInput(hint_text="Nuovo Indirizzo")
        gruppo = TextInput(hint_text="Nuovo Gruppo")
        uso = TextInput(hint_text="Nuovo Uso")
        cliente = TextInput(hint_text="Nuovo Cliente")
        ordine = TextInput(hint_text="Nuovo Ordine")
        for w in [id_input, indirizzo, gruppo, uso, cliente, ordine]:
            layout.add_widget(w)
        btn_save = Button(text="Modifica")

        def edit_utenza(btn):
            self.db.modifica_utenza(int(id_input.text), indirizzo.text, gruppo.text, uso.text, cliente.text, int(ordine.text))
            popup.dismiss()

        btn_save.bind(on_press=edit_utenza)
        layout.add_widget(btn_save)
        popup = Popup(title="Modifica Utenza", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    # Popup per eliminare Utenza
    def delete_utenza_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        id_input = TextInput(hint_text="ID Utenza da eliminare")
        layout.add_widget(id_input)
        btn_delete = Button(text="Elimina")

        def delete_utenza(btn):
            self.db.elimina_utenza(int(id_input.text))
            popup.dismiss()

        btn_delete.bind(on_press=delete_utenza)
        layout.add_widget(btn_delete)
        popup = Popup(title="Elimina Utenza", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    def show_apps(self, instance):
        apps = self.db.lista_app()
        content = "".join([f"{a[0]} - {a[1]}" for a in apps])
        popup = Popup(title="Lista App", content=Label(text=content or "Nessuna App"), size_hint=(0.8, 0.8))
        popup.open()

    def show_utenze(self, instance):
        utenze = self.db.lista_utenze()
        content = "".join([f"{u[0]} - {u[1]}" for u in utenze])
        popup = Popup(title="Lista Utenze", content=Label(text=content or "Nessuna Utenza"), size_hint=(0.8, 0.8))
        popup.open()

    def export_db(self, instance):
        export_path = os.path.join(os.getcwd(), "exported_data.db")
        shutil.copy(DB_FILE, export_path)
        popup = Popup(title="Esportazione", content=Label(text=f"DB esportato in {export_path}"), size_hint=(0.8, 0.8))
        popup.open()

class MyApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    MyApp().run()
