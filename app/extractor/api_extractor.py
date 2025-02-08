from abc import ABC, abstractmethod
from datetime import datetime
from .api_clients import *
from .api_formatter import *

# Responsible for delivering information from the API with an appropriate format using a dataframe

# API Extractor class
class ApiExtractor(ABC):
    @abstractmethod
    def get_data(self, start_date, end_date, interval):
        pass

# Binance API Extractor implementation
class BinanceApiExtractor(ApiExtractor):
    def __init__(self,symbol: str, api_client: ApiClient, formatter=BinanceDataFormatter()):
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


