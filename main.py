from utils.projections import *
from utils.vistas import *
import tkinter as tk

# Configuración de estilos y constantes
ESTILO_ANOTACIONES = dict(boxstyle="round,pad=0.3", fc="beige", ec="black", lw=1)
PALETA = "tab10"
TAMAÑO_VENTANA = "400x300"

def configurar_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación Básica GUI")
    ventana.geometry(TAMAÑO_VENTANA)
    return ventana

def main():
    # ruta_datos = "./datos_aleatorios_temperatura02.xlsx"
    ventana = configurar_ventana()
    menu_principal(ventana)
    ventana.mainloop()

main()