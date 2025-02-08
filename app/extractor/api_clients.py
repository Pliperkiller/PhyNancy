from abc import ABC, abstractmethod
import binance.client as bclient

#Responsible for generating the clients, tools used to provide data from the API

# Abstract class for clients
class ApiClient(ABC):
    @abstractmethod
    def get_klines(self, symbol, interval, start_time, end_time):
        pass

# Client implementation for Binance futures
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

# Client implementation for  Binance Spot
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
