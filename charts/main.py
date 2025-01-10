import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import datetime
import requests

# Crear la aplicación Dash
app = dash.Dash(__name__)

currency = "BTCUSDT"
interval = "15m"
ncandles = 120
ma1 = 9
ma2 = 21
ma3 = 50

# Función para obtener datos actualizados
def get_ohlc_data():
    # Simulando datos reales desde una API
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": currency,
        "interval": interval,  # Intervalo de 1 minuto
        "limit": ncandles       # Últimos 100 datos
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Crear un DataFrame con los datos de OHLC
    ohlc_df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"
    ])
    ohlc_df["timestamp"] = pd.to_datetime(ohlc_df["timestamp"], unit="ms")
    ohlc_df["open"] = ohlc_df["open"].astype(float)
    ohlc_df["high"] = ohlc_df["high"].astype(float)
    ohlc_df["low"] = ohlc_df["low"].astype(float)
    ohlc_df["close"] = ohlc_df["close"].astype(float)
    return ohlc_df[["timestamp", "open", "high", "low", "close"]]

#Calcular MA
def calculate_MA(serie,n):
    return serie.rolling(window = n).mean()

#Calcular EMA
def calculate_EMA(serie,n):
    return serie.ewm(span=n, adjust=False).mean()

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Gráfico de Velas en Tiempo Real (Bitcoin)", style={'text-align': 'center'}),
    dcc.Graph(id="candlestick-graph"),
    dcc.Interval(
        id="interval-update",
        interval=1000,  # 1000 ms = 1 segundo
        n_intervals=0  # Número de intervalos inicial
    )
])

# Callback para actualizar la gráfica
@app.callback(
    Output("candlestick-graph", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_graph(n):
    # Obtener datos actualizados
    ohlc_df = get_ohlc_data()

    # Crear el gráfico de velas
    fig = go.Figure(data=[go.Candlestick(
        x=ohlc_df["timestamp"],
        open=ohlc_df["open"],
        high=ohlc_df["high"],
        low=ohlc_df["low"],
        close=ohlc_df["close"],
        name = "Valor apertura/cierre"
    )])

    # EMA 1
    fig.add_trace(go.Scatter(
        x=ohlc_df["timestamp"],
        y=calculate_EMA(ohlc_df["close"],ma1),
        mode='lines',
        name=f'Media Móvil Exp ({ma1} períodos)'
    ))

    # EMA 2
    fig.add_trace(go.Scatter(
        x=ohlc_df["timestamp"],
        y=calculate_EMA(ohlc_df["close"],ma2),
        mode='lines',
        name=f'Media Móvil Exp ({ma2} períodos)'
    ))

    # EMA 3
    fig.add_trace(go.Scatter(
        x=ohlc_df["timestamp"],
        y=calculate_EMA(ohlc_df["close"],ma3),
        mode='lines',
        name=f'Media Móvil Exp ({ma3} períodos)'
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        title="Gráfico de Velas de Bitcoin",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)",
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=0.5,
            tickformat="%H:%M",
            dtick=int(interval[:-1])*240000
        )
    )
    return fig

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
