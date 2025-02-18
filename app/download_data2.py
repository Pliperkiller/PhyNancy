from tools import credential_manager as creds
from connections import api_connections as api_cnx
from extractor import api_clients as api_cli, api_extractor as api_xtr
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Límite de requests de Binance (ajustado para velas de 1m)
REQUEST_LIMIT = 1200  # Máximo de requests por minuto
WAIT_TIME = 61  # Tiempo de espera cuando se alcanza el límite
MAX_CANDLES_PER_REQUEST = 1000  # Binance permite hasta 1000 velas por request


def extract_binance_api_data(market='futures', symbol='BTCUSDT', interval='1m', start_date='', end_date='', testnet=False):
    # Leer credenciales
    manager = creds.CredentialsManager(reader=creds.JsonCredentialReader())
    bn_credentials = creds.BinanceCredentialsManager(credentials_manager=manager).credentials

    # Conexión a Binance
    bn_client = api_cnx.BinanceConnectionManager(credentials=bn_credentials, testnet=testnet).generate_client()

    # Cliente correcto según mercado
    api_candle_client = api_cli.BinanceFuturesClient(client=bn_client) if market == 'futures' else api_cli.BinanceSpotClient(client=bn_client)

    # Extraer datos
    item = api_xtr.BinanceApiExtractor(symbol=symbol, api_client=api_candle_client)
    return item.get_data(interval=interval, start_date=start_date, end_date=end_date)

def get_data_range(start_date, end_date, chunk_size_days=3, max_workers=5, interval='15m', market='futures', symbol='BTCUSDT'):
    # Binance API limit settings
    request_counter = 0
    REQUEST_LIMIT = 1000
    WAIT_TIME = 61
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()  # Convertir a tipo date
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()      # Convertir a tipo date

    date_ranges = []
    current_date = start_date_obj

    # Generar rangos de fechas
    while current_date < end_date_obj:
        start = current_date
        end = min(current_date + timedelta(days=chunk_size_days), end_date_obj)
        date_ranges.append((start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))  # Convertir a string sin horas
        current_date = end

    data_frames = []

    # Paralelización
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_date = {
            executor.submit(extract_binance_api_data, start_date=start, end_date=end, testnet=False, interval=interval, market=market, symbol=symbol): (start, end)
            for start, end in date_ranges
        }

        for future in as_completed(future_to_date):
            start, end = future_to_date[future]
            try:
                print(f"Extracting data from {start} to {end}")
                df = future.result()
                data_frames.append(df)

                # Incrementar el contador de requests
                request_counter += 1
                
                # Verificar si se ha alcanzado el límite de requests
                if request_counter >= REQUEST_LIMIT:
                    print(f"Se alcanzaron {REQUEST_LIMIT} requests. Esperando {WAIT_TIME} segundos...")
                    time.sleep(WAIT_TIME)
                    request_counter = 0  # Reiniciar el contador después de la espera

            except Exception as e:
                print(f"Error extracting data from {start} to {end}: {e}")
                time.sleep(5)  # Esperar antes de reintentar

    return pd.concat(data_frames, ignore_index=True)


def save_df_to_csv(data, filename):
    """Guarda los datos en un CSV."""
    if data.empty:
        print("No data extracted. Skipping save.")
        return

    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
    data.drop_duplicates(inplace=True)
    data.sort_values('open_time', inplace=True)

    # Ajuste de zona horaria
    localtime = datetime.now(timezone.utc).astimezone()
    UTCdiff = localtime.utcoffset().total_seconds() / 3600
    data['open_time'] = pd.to_datetime(data['open_time']) + pd.to_timedelta(UTCdiff, unit='h')
    data['close_time'] = pd.to_datetime(data['close_time']) + pd.to_timedelta(UTCdiff, unit='h')

    # Guardar en la carpeta "data"
    actual_path = Path(__file__).resolve()
    parent_folder = actual_path.parent.parent
    file_path = parent_folder / 'data' / filename

    data.to_csv(file_path, index=False)
    print(f"Data saved in {file_path}")


if __name__ == '__main__':
    default_start_date = datetime.now().strftime('%Y-%m-%d')  # Desde hoy
    default_end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Hasta mañana
    default_market = 'futures'
    default_symbol = 'BTCUSDT'
    default_interval = '1m'

    # Solicitar datos al usuario
    market = input(f"Enter market (spot/futures) [default: {default_market}]: ") or default_market
    symbol = input(f"Enter trading pair (e.g., BTCUSDT) [default: {default_symbol}]: ") or default_symbol
    start_date = input(f"Enter start date (YYYY-MM-DD) [default: {default_start_date}]: ") or default_start_date
    end_date = input(f"Enter end date (YYYY-MM-DD) [default: {default_end_date}]: ") or default_end_date
    interval = input(f"Enter interval (e.g., 1m, 15m) [default: {default_interval}]: ") or default_interval

    default_file_name = f"{symbol}_{market}_{interval}_{start_date}_{end_date}.csv"
    file_name = input(f"Enter file name [default: {default_file_name}]: ") or default_file_name

    # Extraer datos
    data = get_data_range(start_date, end_date, interval=interval, market=market, symbol=symbol)
    save_df_to_csv(data, file_name)

    print(data)
