from tools import credential_manager as creds
from connections import api_connections as api_cnx
from extractor import api_clients as api_cli, api_extractor as api_xtr
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time



def extract_binance_api_data(market='futures', symbol='BTCUSDT', interval='15m', start_date='2025-02-01', end_date='2026-01-01', testnet=False):
    # Read credentials
    manager = creds.CredentialsManager(reader=creds.JsonCredentialReader())
    bn_credentials = creds.BinanceCredentialsManager(credentials_manager=manager).credentials

    # Generate connection to Binance
    bn_client = api_cnx.BinanceConnectionManager(credentials=bn_credentials, testnet=testnet).generate_client()

    # Correct client assignment
    if market == 'spot':
        api_candle_client = api_cli.BinanceSpotClient(client=bn_client)
    else:
        api_candle_client = api_cli.BinanceFuturesClient(client=bn_client)

    item = api_xtr.BinanceApiExtractor(symbol=symbol, api_client=api_candle_client)
    return item.get_data(interval=interval, start_date=start_date, end_date=end_date)


def get_data_range(start_date, end_date, chunk_size_days=3, max_workers=5, interval='15m',market='futures',symbol ='BTCUSDT'):
    #Binance api limit settings
    request_counter = 0
    REQUEST_LIMIT = 4000
    WAIT_TIME = 61
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    date_ranges = []
    current_date = start_date_obj

    # Generar rangos de fechas
    while current_date < end_date_obj:
        start = current_date
        end = min(current_date + timedelta(days=chunk_size_days), end_date_obj)
        date_ranges.append((start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        current_date = end

    data_frames = []

    # Paralelización
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_date = {
            executor.submit(extract_binance_api_data, start_date=start, end_date=end, testnet=False, interval=interval,market = market,symbol = symbol): (start, end)
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



def first_day_of_year():
    return datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')


def second_day_of_next_month():
    today = datetime.now()
    first_day_next_month = datetime(today.year + (today.month // 12), (today.month % 12) + 1, 1)
    second_day = first_day_next_month + timedelta(days=1)
    return second_day.strftime('%Y-%m-%d')


def save_df_to_csv(data, filename):
    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
    data.drop_duplicates(inplace=True)
    data.sort_values('open_time', inplace=True)
    localtime = datetime.now(timezone.utc).astimezone()
    UTCdiff = localtime.utcoffset().total_seconds() / 3600
    data['open_time'] = pd.to_datetime(data['open_time'])+pd.to_timedelta(UTCdiff, unit='h')
    data['close_time'] = pd.to_datetime(data['close_time'])+pd.to_timedelta(UTCdiff, unit='h')
    actual_path = Path(__file__).resolve()
    parent_folder = actual_path.parent.parent
    file_path = parent_folder / 'data' / filename
    data.to_csv(file_path, index=False)
    print(f"Data saved in {file_path}")


if __name__ == '__main__':
    default_start_date = first_day_of_year()
    default_end_date = second_day_of_next_month()
    default_market = 'futures'
    default_symbol = 'BTCUSDT'
    default_interval = '15m'
    # Request data from the user
    market = input(f"Enter the market (spot or futures) or press Enter to use the default market ({default_market}): ")
    symbol = input(f"Enter the pair (e.g., BTCUSDT) or press Enter to use the default pair ({default_symbol}): ")
    start_date = input(f"Enter the start date (YYYY-MM-DD) or press Enter to use the default date ({default_start_date}): ")
    end_date = input(f"Enter the end date (YYYY-MM-DD) or press Enter to use the default date({default_end_date}): ")
    interval = input(f"Enter the interval (e.g., 1m, 15m) or press Enter to use the default ({default_interval}): ")

    market = market if market else default_market
    symbol = symbol if symbol else default_symbol
    start_date = start_date if start_date else default_start_date
    end_date = end_date if end_date else default_end_date
    interval = interval if interval else default_interval


    default_file_name = f"{symbol}_{market}_{interval}_{start_date}_{end_date}.csv"
    file_name = input(f"Enter the file name or press Enter to use the default({default_file_name}): ")

    # Assign default values if inputs are empty
    start_date = start_date if start_date else first_day_of_year()
    end_date = end_date if end_date else second_day_of_next_month()
    interval = interval if interval else '15m'
    file_name = file_name if file_name else default_file_name

    data = get_data_range(start_date, end_date, interval=interval,market=default_market,symbol=default_symbol)
    save_df_to_csv(data, file_name)

    print(data)
