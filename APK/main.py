
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
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

    def aggiungi_app(self, nome, descrizione):
        self.cursor.execute("INSERT INTO app (nome, descrizione) VALUES (?, ?)", (nome, descrizione))
        self.conn.commit()

    def lista_app(self):
        self.cursor.execute("SELECT * FROM app")
        return self.cursor.fetchall()

    def aggiungi_utenza(self, indirizzo, gruppo, uso, cliente, ordine):
        self.cursor.execute("INSERT INTO utenze (indirizzo, gruppo, uso, cliente, ordine) VALUES (?, ?, ?, ?, ?)",
                            (indirizzo, gruppo, uso, cliente, ordine))
        self.conn.commit()

    def lista_utenze(self):
        self.cursor.execute("SELECT * FROM utenze ORDER BY ordine")
        return self.cursor.fetchall()

    def collega_app_utenza(self, id_app, id_utenza):
        self.cursor.execute("INSERT OR IGNORE INTO app_utenze (id_app, id_utenza) VALUES (?, ?)", (id_app, id_utenza))
        self.conn.commit()

    def close(self):
        self.conn.close()

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.db = DBManager()

        self.add_widget(Label(text="Gestione App e Utenze"))

        btn_app = Button(text="Lista App")
        btn_app.bind(on_press=self.show_apps)
        self.add_widget(btn_app)

        btn_utenze = Button(text="Lista Utenze")
        btn_utenze.bind(on_press=self.show_utenze)
        self.add_widget(btn_utenze)

        btn_export = Button(text="Esporta DB")
        btn_export.bind(on_press=self.export_db)
        self.add_widget(btn_export)

    def show_apps(self, instance):
        apps = self.db.lista_app()
        content = "\n".join([f"{a[0]} - {a[1]}" for a in apps])
        popup = Popup(title="Lista App", content=Label(text=content or "Nessuna App"), size_hint=(0.8, 0.8))
        popup.open()

    def show_utenze(self, instance):
        utenze = self.db.lista_utenze()
        content = "\n".join([f"{u[0]} - {u[1]}" for u in utenze])
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
