from tools import credential_manager as creds
from conections import api_conections as api_cnx
from extractor import  api_clients as api_cli ,api_extractor as api_xtr
import pandas as pd
from datetime import datetime, timedelta

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

if __name__ == '__main__':
    start_date = '2025-02-01'
    end_date = '2025-03-01'

    data = get_data_range(start_date, end_date)
    path = r'C:\\Users\\Usuario\Documents\\codeFolder\\nancy\\PhyNancy\\data\\'
    data.to_csv(path+'BTCUSD_futures_15m.csv',index=False)
    print(data)