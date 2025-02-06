from datetime import datetime
from connection_manager import *
import pandas as pd

class ApiExtraction:
    def __init__(self,connection_manager: BinanceConnectionManager,symbol):
        self._client = connection_manager.client
        self._symbol = symbol
        self.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
            'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Volume', 'Taker Buy Quote Volume', 'Ignore']

    def format_api(self,klines):
        columns = self.columns
    
        df = pd.DataFrame(klines, columns=columns)

        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        df['Quote Asset Volume'] = df['Quote Asset Volume'].astype(float)
        df['Number of Trades'] = df['Number of Trades'].astype(int)
        df['Taker Buy Base Volume'] = df['Taker Buy Base Volume'].astype(float)
        df['Taker Buy Quote Volume'] = df['Taker Buy Quote Volume'].astype(float)
        df['Ignore'] = df['Ignore'].astype(int)
        return df
    
    def get_futures(self,start_date, end_date, interval):
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

        klines = self._client.futures_klines(
                symbol=self._symbol,
                interval=interval,
                startTime=start_ts,
                endTime=end_ts,
                limit=1500
            )
        
        return self.format_api(klines)
        
    def get_spot(self,start_date, end_date, interval):
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

        klines = self._client.get_historical_klines(
                symbol=self._symbol,
                interval=interval,
                startTime=start_ts,
                endTime=end_ts,
                limit=1000
            )
        
        return self.format_api(klines)