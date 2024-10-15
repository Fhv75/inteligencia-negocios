import tkinter as tk

def configurar_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación Básica GUI")
    ventana.geometry("400x300")
    return ventana

def crear_ventana(titulo, master, geometry=None):
    ventana = tk.Toplevel(master)
    ventana.title(titulo)
    ventana.geometry(geometry)
    return ventana
