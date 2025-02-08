from tools import credential_manager as creds
from conections import api_conections as api_cnx
from extractor import  api_clients as api_cli ,api_extractor as api_xtr, api_formatter as api_formt

from datetime import datetime, timedelta

if __name__ == '__main__':
    # Read credentials
    manager = creds.CredentialsManager(reader=creds.JsonCredentialReader())
    bn_credentials = creds.BinanceCredentialsManager(credentials_manager=manager).credentials
    pg_credentials = creds.PgCredentialsManager(credentials_manager=manager).credentials

    #Generate conection to binance
    bn_client = api_cnx.BinanceConnectionManager(credentials=bn_credentials,testnet=False).generate_client()

    #Generate client for each market
    bn_client_futures = api_cli.BinanceFuturesClient(client=bn_client) 
    bn_client_spot = api_cli.BinanceSpotClient(client=bn_client)

    #Generate API extractors for symbols
    BTCUSTD_futures = api_xtr.BinanceApiExtractor(symbol='BTCUSDT',api_client=bn_client_futures) 
    BTCUSTD_spot = api_xtr.BinanceApiExtractor(symbol='BTCUSDT',api_client=bn_client_spot) 
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    '''
    BTCUSTD_futures.get_data(interval='1m',
        start_date=start_time.strftime("%Y-%m-%d"),
        end_date= end_time.strftime("%Y-%m-%d")

    '''


    
    print(BTCUSTD_spot.get_data(interval='5m',
        start_date=start_time.strftime("%Y-%m-%d"),
        end_date= end_time.strftime("%Y-%m-%d")
        ))