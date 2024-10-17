import tkinter as tk
from tkinter import ttk
from utils.projections import *
from utils.etl import cargar_datos
from utils.visualization import *

df = None

def menu_principal(ventana):

    def cargar_datos_y_asignar():
        global df
        df = cargar_datos()
        menu_principal(ventana)  # Llama de nuevo a menu_principal para actualizar la interfaz
 
    if df is None:
        boton_cargar = tk.Button(ventana, text="Cargar datos", command=lambda: cargar_datos_y_asignar())
        boton_cargar.pack(pady=10)
    else:
        print(df)

        # Añadir texto que diga "Proyectar Temperaturas"
        texto = tk.Label(ventana, text="Proyectar Temperaturas", font=("Arial", 12))
        texto.pack(pady=10)

        # Crear un frame para organizar las etiquetas y combobox
        frame_filtros = tk.Frame(ventana)
        frame_filtros.pack(pady=10)

        # Texto y combobox para el año
        label_año = tk.Label(frame_filtros, text="Hasta:")
        label_año.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        combo_años = ttk.Combobox(frame_filtros, values=[str(año) for año in range(df["Año"].max() + 1, df["Año"].max() + 6)], state="readonly")
        combo_años.current(0)
        combo_años.grid(row=0, column=1, padx=5, pady=5)

        # Texto y combobox para la ciudad
        label_ciudad = tk.Label(frame_filtros, text="Ciudad:")
        label_ciudad.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        combo_ciudades = ttk.Combobox(frame_filtros, values=sorted(df["Ciudad"].unique()), state="readonly")
        combo_ciudades.current(0)
        combo_ciudades.grid(row=1, column=1, padx=5, pady=5)

        # Texto y combobox para el modelo
        label_modelo = tk.Label(frame_filtros, text="Modelo:")
        label_modelo.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        combo_modelo = ttk.Combobox(frame_filtros, values=["ARIMA", "SARIMA", "Random Forest", "Gradient Boosting"], state="readonly")
        combo_modelo.current(0)
        combo_modelo.grid(row=2, column=1, padx=5, pady=5)

        # Añadir un botón que diga "Proyectar"
        boton_proyectar = tk.Button(ventana, text="Proyectar", command=lambda: 
                                    proyeccion_temperaturas(ventana, df, int(combo_años.get()), combo_ciudades.get(), combo_modelo.get()))
        boton_proyectar.pack(pady=10)

        boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
        boton_salir.pack(pady=10)