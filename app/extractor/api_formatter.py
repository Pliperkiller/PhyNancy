from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

#Responsible of provide column headers and format for data taken from API data provided by the client

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
