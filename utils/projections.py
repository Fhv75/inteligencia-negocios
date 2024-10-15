from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd
import numpy as np

def gradient_boosting_projection(monthly_temp, forecast_months=12, n_lags=3):
    # Preprocesamiento para convertir la serie temporal en un problema supervisado
    data = pd.DataFrame(monthly_temp)
    data.columns = ['Temperatura']
    
    # Crear lags (valores previos) para usar como características
    for lag in range(1, n_lags + 1):
        data[f'Lag_{lag}'] = data['Temperatura'].shift(lag)
    
    data.dropna(inplace=True)

    # Definir las características (X) y el objetivo (y)
    X = data.drop('Temperatura', axis=1)
    y = data['Temperatura']

    # Entrenar el modelo Gradient Boosting
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X, y)

    # Realizar la proyección
    last_known_data = X.iloc[-1].values.reshape(1, -1)
    forecast = []

    for _ in range(forecast_months):
        next_pred = model.predict(last_known_data)[0]
        forecast.append(next_pred)

        # Actualizar los datos para el siguiente mes
        last_known_data = np.roll(last_known_data, -1)
        last_known_data[0, -1] = next_pred

    # Crear una serie con las predicciones y una frecuencia mensual
    forecast_index = pd.date_range(start=monthly_temp.index[-1] + pd.DateOffset(months=1), periods=forecast_months, freq='M')
    forecast_series = pd.Series(forecast, index=forecast_index)

    return forecast_series


def random_forest_projection(monthly_temp, forecast_months=12, n_lags=3):
    # Preprocesamiento para convertir la serie temporal en un problema supervisado
    data = pd.DataFrame(monthly_temp)
    data.columns = ['Temperatura']
    
    # Crear lags (valores previos) para usar como características
    for lag in range(1, n_lags + 1):
        data[f'Lag_{lag}'] = data['Temperatura'].shift(lag)
    
    data.dropna(inplace=True)

    # Definir las características (X) y el objetivo (y)
    X = data.drop('Temperatura', axis=1)
    y = data['Temperatura']

    # Entrenar el modelo Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Realizar la proyección
    last_known_data = X.iloc[-1].values.reshape(1, -1)
    forecast = []

    for _ in range(forecast_months):
        next_pred = model.predict(last_known_data)[0]
        forecast.append(next_pred)

        # Actualizar los datos para el siguiente mes
        last_known_data = np.roll(last_known_data, -1)
        last_known_data[0, -1] = next_pred

    # Crear una serie con las predicciones y una frecuencia mensual
    forecast_index = pd.date_range(start=monthly_temp.index[-1] + pd.DateOffset(months=1), periods=forecast_months, freq='M')
    forecast_series = pd.Series(forecast, index=forecast_index)

    return forecast_series


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