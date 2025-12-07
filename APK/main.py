
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
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

    # Relazioni App-Utenze
    def collega_app_utenza(self, id_app, id_utenza):
        self.cursor.execute("INSERT OR IGNORE INTO app_utenze (id_app, id_utenza) VALUES (?, ?)", (id_app, id_utenza))
        self.conn.commit()

    def lista_app_per_utenza(self, id_utenza):
        self.cursor.execute("SELECT app.id, app.nome FROM app JOIN app_utenze ON app.id = app_utenze.id_app WHERE app_utenze.id_utenza=?", (id_utenza,))
        return self.cursor.fetchall()

    def lista_utenze_per_app(self, id_app):
        self.cursor.execute("SELECT utenze.id, utenze.indirizzo FROM utenze JOIN app_utenze ON utenze.id = app_utenze.id_utenza WHERE app_utenze.id_app=?", (id_app,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class MainTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()
        self.do_default_tab = False
        self.tab_height = '40dp'

        # Tab App
        app_tab = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        app_tab.bind(minimum_height=app_tab.setter('height'))
        scroll_app = ScrollView(size_hint=(1, 1))
        scroll_app.add_widget(app_tab)
        app_tab.add_widget(Button(text="Aggiungi App", size_hint_y=None, height='40dp', on_press=self.add_app_popup))
        app_tab.add_widget(Button(text="Modifica App", size_hint_y=None, height='40dp', on_press=self.edit_app_popup))
        app_tab.add_widget(Button(text="Elimina App", size_hint_y=None, height='40dp', on_press=self.delete_app_popup))
        app_tab.add_widget(Button(text="Lista App", size_hint_y=None, height='40dp', on_press=self.show_apps))
        self.add_widget(scroll_app)
        scroll_app.text = "App"

        # Tab Utenze
        utenze_tab = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        utenze_tab.bind(minimum_height=utenze_tab.setter('height'))
        scroll_utenze = ScrollView(size_hint=(1, 1))
        scroll_utenze.add_widget(utenze_tab)
        utenze_tab.add_widget(Button(text="Aggiungi Utenza", size_hint_y=None, height='40dp', on_press=self.add_utenza_popup))
        utenze_tab.add_widget(Button(text="Modifica Utenza", size_hint_y=None, height='40dp', on_press=self.edit_utenza_popup))
        utenze_tab.add_widget(Button(text="Elimina Utenza", size_hint_y=None, height='40dp', on_press=self.delete_utenza_popup))
        utenze_tab.add_widget(Button(text="Lista Utenze", size_hint_y=None, height='40dp', on_press=self.show_utenze))
        self.add_widget(scroll_utenze)
        scroll_utenze.text = "Utenze"

        # Tab Relazioni
        rel_tab = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        rel_tab.bind(minimum_height=rel_tab.setter('height'))
        scroll_rel = ScrollView(size_hint=(1, 1))
        scroll_rel.add_widget(rel_tab)
        rel_tab.add_widget(Button(text="Collega App-Utenza", size_hint_y=None, height='40dp', on_press=self.link_relation_popup))
        rel_tab.add_widget(Button(text="Mostra App per Utenza", size_hint_y=None, height='40dp', on_press=self.show_apps_for_utenza))
        rel_tab.add_widget(Button(text="Mostra Utenze per App", size_hint_y=None, height='40dp', on_press=self.show_utenze_for_app))
        self.add_widget(scroll_rel)
        scroll_rel.text = "Relazioni"

        # Tab Esportazione
        export_tab = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        export_tab.bind(minimum_height=export_tab.setter('height'))
        scroll_export = ScrollView(size_hint=(1, 1))
        scroll_export.add_widget(export_tab)
        export_tab.add_widget(Button(text="Esporta DB", size_hint_y=None, height='40dp', on_press=self.export_db))
        self.add_widget(scroll_export)
        scroll_export.text = "Esporta"

    # Funzioni popup (riuso delle precedenti)
    def add_app_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
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
        popup = Popup(title="Aggiungi App", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def show_apps(self, instance):
        apps = self.db.lista_app()
        content = "".join([f"{a[0]} - {a[1]}" for a in apps])
        popup = Popup(title="Lista App", content=Label(text=content or "Nessuna App"), size_hint=(0.9, 0.9))
        popup.open()

    def export_db(self, instance):
        export_path = os.path.join(os.getcwd(), "exported_data.db")
        shutil.copy(DB_FILE, export_path)
        popup = Popup(title="Esportazione", content=Label(text=f"DB esportato in {export_path}"), size_hint=(0.9, 0.9))
        popup.open()

class MyApp(App):
    def build(self):
        return MainTabbedPanel()

if __name__ == "__main__":
    MyApp().run()
