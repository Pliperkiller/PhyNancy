from binance.client import Client
import psycopg2
import time
import pandas as pd
import json
import os

def read_folder_file(folder_name, file_name):
    dir_path = os.path.dirname(os.getcwd())
    folders = [folder for folder in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, folder))]

    for folder in folders:
        if folder == folder_name:
            folder_path = os.path.join(dir_path, folder)
            files = [file for file in os.listdir(folder_path)]

            for file in files:
                if file==file_name:
                    return os.path.join(folder_path,file_name)

    return None

def get_credentials(service_name,json_path):
    with open(json_path, "r") as file:
        data = json.load(file)

    passwords = data.get("passwords", [])

    for entry in passwords:
        if entry["service"] == service_name:
            return entry
    return None


def insert_to_db(candle,conn,cursor,table_name):
    query = f"""
        INSERT INTO public.{table_name}(
        open_time, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_volume, taker_buy_quote_volume, ignore)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (open_time) DO NOTHING;
    """
    cursor.execute(query, candle)
    conn.commit()

def truncate_table(table_name,conn,cursor):
    truncate_query = f"TRUNCATE TABLE public.{table_name};"
    cursor.execute(truncate_query)
    print(cursor.statusmessage)
    conn.commit()
    

def merge_tables(source_table_name,live_table_name,conn,cursor):
    truncate_query = f"""
    MERGE INTO {live_table_name} AS lve
    USING {source_table_name} AS src
    ON lve.open_time = src.open_time
    
    WHEN MATCHED THEN
        UPDATE SET 
        open_time=src.open_time, 
        open=src.open, 
        high=src.high, 
        low=src.low, 
        close=src.close, 
        volume=src.volume, 
        close_time=src.close_time, 
        quote_asset_volume=src.quote_asset_volume, 
        number_of_trades=src.number_of_trades, 
        taker_buy_base_volume=src.taker_buy_base_volume, 
        taker_buy_quote_volume=src.taker_buy_quote_volume, 
        ignore=src.ignore

    WHEN NOT MATCHED THEN
        INSERT (open_time, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_volume, taker_buy_quote_volume, ignore)
        VALUES (
        src.open_time, 
        src.open, 
        src.high,
        src.low, 
        src.close, 
        src.volume, 
        src.close_time, 
        src.quote_asset_volume, 
        src.number_of_trades, 
        src.taker_buy_base_volume, 
        src.taker_buy_quote_volume, 
        src.ignore);
    """
    cursor.execute(truncate_query)
    print(cursor.statusmessage)
    conn.commit()

def api_to_df(klines,columns):
    df = pd.DataFrame(klines, columns=columns)

    # Format data
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


def get_last_candles(symbol: str,limit: int,interval: str, client)-> pd.DataFrame:

    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
            'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Volume', 'Taker Buy Quote Volume', 'Ignore']
    df = api_to_df(klines,columns)
    return df

def get_historic_candles(symbol: str,initial_date: str,end_date: str,interval: str, client)-> pd.DataFrame:

    klines = client.get_historical_klines(symbol, interval, initial_date,end_date)
    columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
            'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Volume', 'Taker Buy Quote Volume', 'Ignore']
    df = api_to_df(klines,columns)
    return df


def get_latest_date(table_name,conn,cursor):
    query = f"SELECT MIN(open_time) FROM public.{table_name};"
    cursor.execute(query)
    oldest_date = cursor.fetchone()[0]
    return oldest_date

