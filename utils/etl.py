import pandas as pd
from tkinter import filedialog

def cargar_datos():
    # Cargar el archivo de Excel
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de datos", 
        filetypes=(("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
    )
    df = pd.read_excel(ruta)

    # Intentar convertir la columna 'Fecha' a datetime y tratar los errores
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    # Verificar si hay valores no convertidos (NaT)
    if df['Fecha'].isna().sum() > 0:
        print("Problemas encontrados en la columna 'Fecha'.")
        print(df[df['Fecha'].isna()])  # Mostrar las filas problemáticas para revisar manualmente
    else:
        print("Todas las fechas han sido convertidas correctamente.")

    # Si no hay problemas, continuar con el procesamiento
    if df['Fecha'].isna().sum() == 0:
        df.set_index('Fecha', inplace=True)
        return preprocesar_datos(df)
    else:
        raise ValueError("Hay valores problemáticos en la columna de fechas que necesitan revisión.")

def preprocesar_datos(df):
    df["Año"] = df.index.year
    df["Mes"] = df.index.month
    return df