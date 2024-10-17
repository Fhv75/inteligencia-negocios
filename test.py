import pandas as pd
# Cargar datos_sept2019_sept2024.xlsx

df = pd.read_excel("datos_sept2019_sept2024.xlsx")

print(df["Fecha"].min())
print(df["Fecha"].max())

print(df["Temperatura"].min())
print(df["Temperatura"].max())

# Convertir hora a datetime


print(df["Hora"].min())
print(df["Hora"].max())