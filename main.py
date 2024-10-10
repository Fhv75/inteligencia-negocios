from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns   

# Configuración de estilos y constantes
ESTILO_ANOTACIONES = dict(boxstyle="round,pad=0.3", fc="beige", ec="black", lw=1)
PALETA = "tab10"
TAMAÑO_VENTANA = "400x300"

def cargar_datos(ruta):
    dataframe = pd.read_excel(ruta)
    return preprocesar_datos(dataframe)

def preprocesar_datos(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d")
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    return df

def configurar_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación Básica GUI")
    ventana.geometry(TAMAÑO_VENTANA)
    return ventana

def vista_principal(ventana, df): 
    boton_promedios = tk.Button(ventana, text="Mostrar promedios", command=lambda: mostrar_promedios(ventana, df))
    boton_promedios.pack(pady=10)

    # Añadir texto que diga "Proyectar Temperaturas"
    texto = tk.Label(ventana, text="Proyectar Temperaturas", font=("Arial", 12))
    texto.pack(pady=10)

    # Añadir un combox para años y ciudades
    # La opciones de años contienen los 5 años subsiguientes al maximo en el dataset
    opciones_años = [str(año) for año in range(df["Año"].max() + 1, df["Año"].max() + 6)]
    opciones_ciudades = df["Ciudad"].unique().tolist()
    opciones_ciudades.sort()

    combo_años = ttk.Combobox(ventana, values=opciones_años, state="readonly")
    combo_años.current(0)
    combo_años.pack(pady=10)

    combo_ciudades = ttk.Combobox(ventana, values=opciones_ciudades, state="readonly")
    combo_ciudades.current(0)
    combo_ciudades.pack(pady=10)

    combo_modelo = ttk.Combobox(ventana, values=["ARIMA", "SARIMA", "Random Forest", "Gradient Boosting"], state="readonly")
    combo_modelo.current(0)
    combo_modelo.pack(pady=10)

    # Añadir un botón que diga "Proyectar"
    boton_proyectar = tk.Button(ventana, text="Proyectar", command=lambda: 
                                proyeccion_temperaturas(ventana, df, int(combo_años.get()), combo_ciudades.get(), combo_modelo.get()))
    boton_proyectar.pack(pady=10)

    boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
    boton_salir.pack(pady=10)

def mostrar_promedios(ventana, df):
    promedios = df.groupby(["Ciudad", "Año"])["Temperatura"].mean().reset_index()
    nueva_ventana = crear_ventana("Promedios de temperatura", ventana)
    
    fig, ax = plt.subplots()
    crear_grafico_barras(promedios, ax)
    agregar_anotaciones(ax, fig)

    mostrar_canvas(fig, nueva_ventana)

def crear_ventana(titulo, master, geometry=None):
    ventana = tk.Toplevel(master)
    ventana.title(titulo)
    ventana.geometry(geometry)
    return ventana

def crear_grafico_barras(data, ax):
    sns.barplot(data=data, x="Año", y="Temperatura", hue="Ciudad", ax=ax, palette=PALETA)
    ax.set_title("Promedios de temperatura por año", fontsize=14, fontweight='bold')
    ax.set_ylabel("Temperatura", fontsize=12)
    ax.set_xlabel("Año", fontsize=12)
    plt.xticks(rotation=30)
    ax.legend(title="Ciudad", bbox_to_anchor=(1, 1), loc='upper left')
    plt.tight_layout()

def arima_projection(monthly_temp, forecast_months=12):
    # Entrenar un modelo ARIMA - seleccionar un orden inicial básico (p,d,q)
    model = ARIMA(monthly_temp, order=(1, 1, 1))
    model_fit = model.fit()
    
    # Realizar la proyección para los próximos 'forecast_months' meses
    forecast = model_fit.forecast(steps=forecast_months)
    
    return forecast

def sarima_projection(monthly_temp, forecast_months=12, seasonal_order=(1, 1, 1, 12)):
    import itertools
    # Entrenar un modelo SARIMA con el orden estacional especificado
    model = SARIMAX(monthly_temp, order=(1, 1, 1), seasonal_order=seasonal_order)
    model_fit = model.fit(disp=False)

    # Realizar la proyección para los próximos 'forecast_months' meses
    forecast = model_fit.forecast(steps=forecast_months)
    return forecast

def proyeccion_temperaturas(ventana, df, año, ciudad, modelo):
    # Filtrar los datos por la ciudad y los años hasta el seleccionado
    df_city = df[(df['Ciudad'] == ciudad)]
    # Agrupar por mes y calcular la temperatura promedio mensual, asociando el año-mes con el promedio
    monthly_temp = df_city.groupby(['Año', 'Mes'])['Temperatura'].mean()
    # Reindexar el DataFrame para tener un índice de fechas con el formato YYYY-MM
    monthly_temp.index = pd.to_datetime(monthly_temp.index.map(lambda x: f"{x[0]}-{x[1]}"))

    forecast=None
    forecast_months = (año - monthly_temp.index[-1].year) * 12

    if modelo == "ARIMA":
        forecast = arima_projection(monthly_temp, forecast_months)
        # Reindexar el forecast para tener un índice de fechas con el formato YYYY-MM
        forecast.index = pd.date_range(start=monthly_temp.index[-1], periods=len(forecast), freq='M')[0:]   

    elif modelo == "SARIMA":
        forecast = sarima_projection(monthly_temp, forecast_months)
        # Reindexar el forecast para tener un índice de fechas con el formato YYYY-MM
        forecast.index = pd.date_range(start=monthly_temp.index[-1], periods=len(forecast), freq='M')[0:]
    elif modelo == "Random Forest":
        pass
    elif modelo == "Gradient Boosting":
        pass
    

    nueva_ventana = crear_ventana("Proyección de temperaturas", ventana)
    fig, ax = plt.subplots()
    sns.lineplot(x=monthly_temp.index, y=monthly_temp, label='Datos Históricos', color='orange')
    sns.lineplot(x=forecast.index, y=forecast, label='Proyección ARIMA', linestyle='--', color='orange')
    plt.title(f'Proyección de Temperatura para {ciudad} ({año})')
    plt.ylabel('Temperatura (°C)')
    plt.xlabel('Fecha')
    plt.xticks(rotation=30)
    ax.legend(title="Ciudad", bbox_to_anchor=(1, 1), loc='upper left')
    ax.grid(alpha=0.2)
    plt.tight_layout()

    mostrar_canvas(fig, nueva_ventana)

def agregar_anotaciones(ax, fig):
    anotaciones = []
    for p in ax.patches:
        annotation = ax.annotate(f"{p.get_height():.1f}",
                                 (p.get_x() + p.get_width() / 2., p.get_height()),
                                 ha='center', va='center', fontsize=9, color='black',
                                 bbox=ESTILO_ANOTACIONES,
                                 visible=False)
        anotaciones.append(annotation)

    def on_move(event):
        visibilidad_cambiada = False
        for p, annotation in zip(ax.patches, anotaciones):
            if p.contains_point((event.x, event.y)):
                annotation.set_visible(True)
                visibilidad_cambiada = True
            else:
                annotation.set_visible(False)
                
        if visibilidad_cambiada:
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_move)

def mostrar_canvas(fig, ventana):
    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack()

def main():
    ruta_datos = "./datos_aleatorios_temperatura02.xlsx"
    df = cargar_datos(ruta_datos)
    ventana = configurar_ventana()
    vista_principal(ventana, df)
    ventana.mainloop()

main()
