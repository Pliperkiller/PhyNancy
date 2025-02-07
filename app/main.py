from tools import credential_manager as creds
from tools import api_manager as api
from datetime import datetime, timedelta

if __name__ == '__main__':
    reader = creds.JsonCredentialReader() 
    manager = creds.CredentialsManager(reader=reader)
    bn_credentials = creds.BinanceCredentialsManager(credentials_manager=manager).credentials
    pg_credentials = creds.PgCredentialsManager(credentials_manager=manager).credentials

    bn_client = api.BinanceConnectionManager(credentials=bn_credentials,testnet=False).generate_client()
    bn_client_futures = api.BinanceFuturesClient(client=bn_client) 
    bn_client_spot = api.BinanceSpotClient(client=bn_client)

    BTCUSTD_futures = api.ApiExtractor(symbol='BTCUSDT',api_client=bn_client_futures,formatter=api.BinanceDataFormatter()) 
    BTCUSTD_spot = api.ApiExtractor(symbol='BTCUSDT',api_client=bn_client_spot,formatter=api.BinanceDataFormatter()) 
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    print(BTCUSTD_futures.get_data(interval='1h',
        start_date=start_time.strftime("%Y-%m-%d"),
        end_date= end_time.strftime("%Y-%m-%d")
        ))

    print(BTCUSTD_spot.get_data(interval='1h',
        start_date=start_time.strftime("%Y-%m-%d"),
        end_date= end_time.strftime("%Y-%m-%d")
        ))