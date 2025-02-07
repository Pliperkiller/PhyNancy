from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import binance.client as bclient

###Connections
# Abstract class for API connection
class ConnectionManager(ABC):
    @abstractmethod
    def generate_client(self):
        pass

# Binance api implementation
class BinanceConnectionManager(ConnectionManager):
    def __init__(self, credentials, testnet=True):
        self.credentials = credentials
        self.testnet = testnet

    def generate_client(self):
        return bclient.Client(
            api_key = self.credentials['api_key'],
            api_secret= self.credentials['api_secret'],
            testnet=self.testnet
        )


##Clients
# Abstract class for clients
class ApiClient(ABC):
    @abstractmethod
    def get_klines(self, symbol, interval, start_time, end_time):
        pass

# Client for Binance futures
class BinanceFuturesClient(ApiClient):
    def __init__(self, client:bclient.Client):
        self.client = client

    def get_klines(self, symbol, interval, start_time, end_time):
        return self.client.futures_klines(
            symbol=symbol,
            interval=interval,
            startTime=start_time,
            endTime=end_time,
            limit=1500
        )

# Client for  Binance Spot
class BinanceSpotClient(ApiClient):
    def __init__(self, client:bclient.Client):
        self.client = client

    def get_klines(self, symbol, interval, start_time, end_time):
        return self.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_time,
            end_str=end_time,
            limit=1000
        )



### Data formatters
# Abstraction for data formatters
class DataFormatter(ABC):
    @abstractmethod
    def format(self, data):
        pass

# Binance api formatter
class BinanceDataFormatter(DataFormatter):
    COLUMNS = [
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
        'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Volume',
        'Taker Buy Quote Volume', 'Ignore',
    ]

    def format(self, klines):
        df = pd.DataFrame(klines, columns=BinanceDataFormatter.COLUMNS)
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

        float_columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                          'Quote Asset Volume', 'Taker Buy Base Volume',
                          'Taker Buy Quote Volume']
        int_columns = ['Number of Trades', 'Ignore']

        for col in float_columns:
            df[col] = df[col].astype(float)
        for col in int_columns:
            df[col] = df[col].astype(int)

        return df


# API Extractor class
class ApiExtractor:
    def __init__(self,symbol: str, api_client: ApiClient, formatter: DataFormatter):
        self.api_client = api_client
        self.formatter = formatter
        self.symbol = symbol

    def get_data(self, start_date, end_date, interval):
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

        klines = self.api_client.get_klines(
            symbol=self.symbol,
            interval=interval,
            start_time=start_ts,
            end_time=end_ts
        )

        return self.formatter.format(klines)

