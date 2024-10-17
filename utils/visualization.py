import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.projections import *
from utils.gui_helpers import *
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

ESTILO_ANOTACIONES = dict(boxstyle="round,pad=0.3", fc="beige", ec="black", lw=1)
PALETA = "tab10"
TAMAÑO_VENTANA = "400x300"

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

def proyeccion_temperaturas(ventana, df, año, ciudad, modelo):
    # Filtrar los datos por la ciudad
    df_city = df[df['Ciudad'] == ciudad]
    
    # Agrupar por año-mes y calcular la temperatura promedio mensual
    monthly_temp = df_city.groupby(['Año', 'Mes'])['Temperatura'].mean()
    
    # Reindexar el DataFrame para tener un índice de fechas con el formato YYYY-MM
    monthly_temp.index = pd.to_datetime(monthly_temp.index.map(lambda x: f"{x[0]}-{x[1]}"))
    monthly_temp = monthly_temp.asfreq('MS')  # Establecer frecuencia mensual (MS = Start of Month)

    forecast = None
    forecast_months = (año - monthly_temp.index[-1].year) * 12

    # Proyecciones usando el modelo seleccionado
    if modelo == "ARIMA":
        forecast = arima_projection(monthly_temp, forecast_months)
    elif modelo == "SARIMA":
        forecast = sarima_projection(monthly_temp, forecast_months)
    elif modelo == "Random Forest":
        forecast = random_forest_projection(monthly_temp, forecast_months)
    elif modelo == "Gradient Boosting":
        forecast = gradient_boosting_projection(monthly_temp, forecast_months)

    # Reindexar el forecast para tener un índice de fechas con el formato YYYY-MM
    if forecast is not None:
        # Crear ventana y gráfico para mostrar la proyección
        nueva_ventana = crear_ventana("Proyección de temperaturas", ventana)
        
        # Crear la figura y el canvas para mostrar el gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Dibujar las líneas de datos históricos y proyecciones
        line_hist, = ax.plot(monthly_temp.index, monthly_temp, label='Datos Históricos', color='orange')
        line_forecast, = ax.plot(forecast.index, forecast, label='Proyección ' + modelo, linestyle='--', color='orange')
        
        ax.set_title(f'Proyección de Temperatura para {ciudad} ({año})')
        ax.set_ylabel('Temperatura (°C)')
        ax.set_xlabel('Fecha')
        ax.legend(title="Ciudad", bbox_to_anchor=(1, 1), loc='upper left')
        ax.grid(alpha=0.2)
        plt.xticks(rotation=30)
        plt.tight_layout()

        # Mostrar el gráfico en la ventana
        canvas = FigureCanvasTkAgg(fig, master=nueva_ventana)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Crear la anotación para mostrar en el hover
        annot = ax.annotate("", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        # Obtener los datos de las líneas
        x_data_hist = line_hist.get_xdata()
        y_data_hist = line_hist.get_ydata()

        x_data_forecast = line_forecast.get_xdata()
        y_data_forecast = line_forecast.get_ydata()

        # Función para actualizar la anotación
        def update_annot(ind, line_type):
            index = ind["ind"][0]
            if line_type == "hist":
                x_value = x_data_hist[index]
                y_value = y_data_hist[index]
                label = "Histórico"
            else:
                x_value = x_data_forecast[index]
                y_value = y_data_forecast[index]
                label = "Proyección"

            # Convertir numpy.datetime64 a datetime de Python y formatear la fecha
            x_value = pd.to_datetime(x_value).to_pydatetime()
            annot.xy = (x_value, y_value)
            text = f"{label}\nFecha: {x_value.strftime('%Y-%m')}\nTemp: {y_value:.2f} °C"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.8)

        # Evento para manejar el movimiento del ratón
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                # Verificar si el ratón está cerca de algún punto de la línea histórica
                cont_hist, ind_hist = line_hist.contains(event)
                if cont_hist:
                    update_annot(ind_hist, "hist")
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    # Verificar si el ratón está cerca de algún punto de la línea de proyección
                    cont_forecast, ind_forecast = line_forecast.contains(event)
                    if cont_forecast:
                        update_annot(ind_forecast, "forecast")
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    elif vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        # Conectar el evento de movimiento del ratón al gráfico
        fig.canvas.mpl_connect("motion_notify_event", hover)

        # Calcular los promedios anuales de los años proyectados
        forecast_df = forecast.reset_index()
        forecast_df.columns = ['Fecha', 'Temperatura']
        forecast_df['Año'] = forecast_df['Fecha'].dt.year
        promedios_anuales = forecast_df.groupby('Año')['Temperatura'].mean()

        # Calcular promedios anuales de los años historicos
        promedios_anuales_hist = monthly_temp.reset_index()
        promedios_anuales_hist.columns = ['Fecha', 'Temperatura']
        promedios_anuales_hist['Año'] = promedios_anuales_hist['Fecha'].dt.year
        promedios_anuales_hist = promedios_anuales_hist.groupby('Año')['Temperatura'].mean()


        # Calcular métricas de error (MAE y RMSE)
        if len(monthly_temp) >= forecast_months:  # Para asegurarnos de tener datos suficientes para la comparación
            comparacion_historica = monthly_temp[:forecast_months]
            comparacion_forecast = forecast[:len(comparacion_historica)]

            mae = mean_absolute_error(comparacion_historica, comparacion_forecast)
            rmse = np.sqrt(mean_squared_error(comparacion_historica, comparacion_forecast))
        else:
            mae = rmse = None

        # Crear un frame para organizar la información en dos columnas con una distribución correcta
        frame_resultados = tk.Frame(nueva_ventana)
        frame_resultados.pack(pady=10, padx=10, fill='x')

        # Añadir los promedios anuales a la primera columna (alineados a la izquierda)
        promedios_texto = "Promedios Anuales:\n"
        for año, promedio in promedios_anuales_hist.items():
            promedios_texto += f"Año {año}: {promedio:.2f} °C\n"
        for año, promedio in promedios_anuales.items():
            promedios_texto += f"Año {año}: {promedio:.2f} °C\n"
    

        label_promedios = tk.Label(frame_resultados, text=promedios_texto, font=("Arial", 12), justify="left", anchor="w")
        label_promedios.grid(row=0, column=0, sticky="w")

        # Añadir las métricas de error a la segunda columna (alineadas a la derecha)
        if mae is not None and rmse is not None:
            metricas_texto = "Métricas de Error:\n"
            metricas_texto += f"MAE: {mae:.2f}\nRMSE: {rmse:.2f}\n"
        else:
            metricas_texto = "Métricas de Error:\nNo se pueden calcular MAE y RMSE con los datos actuales."

        label_metricas = tk.Label(frame_resultados, text=metricas_texto, font=("Arial", 12), justify="right", anchor="e")
        label_metricas.grid(row=0, column=1, sticky="e", padx=(50, 0))

        # Configuración para expandir las columnas correctamente
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_columnconfigure(1, weight=1)


