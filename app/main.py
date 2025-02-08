from tools import credential_manager as creds
from conections import api_conections as api_cnx
from extractor import  api_clients as api_cli ,api_extractor as api_xtr

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


if __name__ == '__main__':
    start_date = '2025-02-01'
    end_date = '2025-03-01'

    data = extract_binance_api_data(start_date=start_date, end_date=end_date,testnet = False)
    print(data)