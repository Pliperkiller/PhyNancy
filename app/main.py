from tools import credential_manager as creds
from connections import api_connections as api_cnx
from extractor import  api_clients as api_cli ,api_extractor as api_xtr
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def extract_binance_api_data(market='futures', symbol = 'BTCUSDT', interval = '15m', start_date = '2025-02-01' , end_date='2026-01-01',  **kwargs):
    for key, value in kwargs.items():
        if key=='testnet': testnet = value
    
    # Read credentials
    manager = creds.CredentialsManager(reader=creds.JsonCredentialReader())
    bn_credentials = creds.BinanceCredentialsManager(credentials_manager=manager).credentials

    #Generate conection to binance
    bn_client = api_cnx.BinanceConnectionManager(credentials=bn_credentials,testnet=testnet).generate_client()

    if market == 'spot':
        api_clandle_client = api_cli.BinanceFuturesClient(client=bn_client) 
    if market == 'futures':
        api_clandle_client = api_cli.BinanceSpotClient(client=bn_client)
    
    item = api_xtr.BinanceApiExtractor(symbol='BTCUSDT',api_client=api_clandle_client) 

    return item.get_data( interval=interval,start_date=start_date, end_date= end_date)

def get_data_range(start_date, end_date):
    
    df_general = pd.DataFrame()

    fecha_inicio = datetime.strptime(start_date, '%Y-%m-%d')
    fecha_fin = datetime.strptime(end_date, '%Y-%m-%d')

    
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:

        print(f"Extracting data: {fecha_actual.strftime('%Y-%m-%d')}")

        # Definir el rango del día actual
        inicio_dia = fecha_actual.strftime('%Y-%m-%d')
        fin_dia = (fecha_actual + timedelta(days=1)).strftime('%Y-%m-%d')

        # Llamar a la función para obtener los datos del día
        df_dia = extract_binance_api_data(start_date=inicio_dia, end_date=fin_dia,testnet=False)

        # Concatenar con el DataFrame general
        df_general = pd.concat([df_general, df_dia], ignore_index=True)

        # Avanzar al siguiente día
        fecha_actual += timedelta(days=1)

    return df_general


def first_day_of_year():
    return datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')

def second_day_of_next_month():
    today = datetime.now()
    first_day_next_month = datetime(today.year + (today.month // 12), (today.month % 12) + 1, 1)
    second_day = first_day_next_month + timedelta(days=1)
    return second_day.strftime('%Y-%m-%d')

def save_df_to_csv(data,filename):
    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
    actual_path = Path(__file__).resolve()
    parent_folder = actual_path.parent.parent
    file_path = parent_folder / 'data' / filename
    data.to_csv(file_path, index=False)
    print(f"Data saved in {file_path}")



if __name__ == '__main__':
    # Request data from the user
    start_date = input("Enter the start date (YYYY-MM-DD) or press Enter to use the default date: ")
    end_date = input("Enter the end date (YYYY-MM-DD) or press Enter to use the default date: ")
    file_name = input("Enter the file name or press Enter to use the default: ")

    # Assign default values if inputs are empty
    start_date = start_date if start_date else first_day_of_year()
    end_date = end_date if end_date else second_day_of_next_month()
    file_name = file_name if file_name else 'data.csv'

    data = get_data_range(start_date, end_date)
    save_df_to_csv(data,file_name)

    print(data)