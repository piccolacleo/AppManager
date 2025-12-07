import pandas as pd
import os

# Il file da ispezionare si troverà nella stessa cartella di questo script
BASE_DIR = os.path.dirname(__file__)
XLSX_FILE = os.path.join(BASE_DIR, 'AppCell.xlsx')

print(f"--- Ispezione del file: {XLSX_FILE} ---")

try:
    # Ispezione foglio 'Account'
    df_acc = pd.read_excel(XLSX_FILE, sheet_name='Account')
    print("\n--- Foglio 'Account' ---")
    print("Nomi delle colonne:", df_acc.columns.to_list())
    print("Prime 2 righe:")
    print(df_acc.head(2).to_string())

    # Ispezione foglio 'POCO'
    df_poco = pd.read_excel(XLSX_FILE, sheet_name='POCO')
    print("\n--- Foglio 'POCO' ---")
    print("Nomi delle colonne:", df_poco.columns.to_list())
    print("Prime 2 righe:")
    print(df_poco.head(2).to_string())

except FileNotFoundError:
    print(f"\nERRORE: File non trovato. Assicurati che '{XLSX_FILE}' esista.")
except Exception as e:
    print(f"\nERRORE durante la lettura del file: {e}")
