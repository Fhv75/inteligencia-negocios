import pandas as pd
from tkinter import filedialog

def cargar_datos():
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de datos", 
        filetypes=(("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
    dataframe = pd.read_excel(ruta)
    return preprocesar_datos(dataframe)

def preprocesar_datos(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d")
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    return df