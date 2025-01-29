import psycopg2
import os
import json
import binance.client as bclient
import pandas as pd
from datetime import datetime

    ###########################################
    ########### CREDENTIALS ###################
    ###########################################
class CredentialsManager:
    def __init__(self,folder_name = 'keys',file_name = 'keys.json'):
        self._folder_name = folder_name
        self._file_name = file_name
        self.credentials_path = self.read_credentials() if self.read_credentials else print('No credentials')
        self.credentials_list = self.get_credentials()


    def read_credentials(self):
        folder_name, file_name = self._folder_name, self._file_name
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

    def get_credentials(self):
        json_path = self.credentials_path
        with open(json_path, "r") as file:
            data = json.load(file)

        return data


    def get_service_credentials(self,service_name,group="passwords"):
            passwords = self.credentials_list.get(group, [])
            for entry in passwords:
                if entry["service"] == service_name:
                    return entry
                
            return None
    
class CredentialsManagerBase:
    def __init__(self, manager: CredentialsManager, service_name: str, required_keys: list):
        self._manager = manager.get_service_credentials(service_name)
        self.required_keys = required_keys
        self.set_credentials()

    def set_credentials(self):
        try:
            for key in self.required_keys:
                setattr(self, key, self._manager[key])
            
            print('Credentials set')
        
        except KeyError as e:
            print(f"Missing key in credentials: {e}")
        except Exception as e:
            print(f"Error setting credentials: {e}")

class BinanceCredentialsManager(CredentialsManagerBase):
    def __init__(self, manager: CredentialsManager, service_name='FuturesTestnet'):
        required_keys = ['api_key', 'api_secret']
        super().__init__(manager, service_name, required_keys)

class PgCredentialsManager(CredentialsManagerBase):
    def __init__(self, manager: CredentialsManager, service_name='pgcurrencies'):
        required_keys = ['hostname', 'database', 'port', 'username', 'password']
        super().__init__(manager, service_name, required_keys)





    ###########################################
    ########### CONNECTIONS ###################
    ###########################################


class PgConnecionManager:
    def __init__(self,credentials: PgCredentialsManager):
        self._credentials = credentials
        self.connection = None
        self.connect() 
    
    @property
    def is_connected(self):
        return (
            self.connection is not None 
            and not self.connection.closed 
        )

    def disconnect(self):
            
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
            self.connection = None

        if not self.is_connected:
            print("Disconnection successful")


    def connect(self):
        if self.connection: self.disconnect()
        
        try:
            self.connection = psycopg2.connect(
                host=self._credentials.hostname,
                database=self._credentials.database,
                port=self._credentials.port,
                user=self._credentials.username,
                password=self._credentials.password
            )
            print("Connection sucessful")
        except psycopg2.Error as e:
            print(f"Connection : {e}")
            self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        self.disconnect()


class BinanceConnectionManager:
    def __init__(self,credentials: BinanceCredentialsManager, testnet=True):
        self._credentials = credentials
        self.client = bclient.Client(credentials.api_key, credentials.api_secret,testnet=testnet)


    ###########################################
    ########### SQL Queries ###################
    ###########################################

class TruncateQueriesManager:
    def __init__(self,connection :PgConnecionManager, prefact_table: str):
        self._connection = connection
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):
        self.query = f"TRUNCATE TABLE public.{self._prefact};"

    def truncate_table(self):
        
        try:
            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(self.query)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data truncation: {e}")

        finally:
            if cursor:
                cursor.close()


class InsertQueriesManager:
    def __init__(self,df: pd.DataFrame, connection: PgConnecionManager, prefact_table: str):
        self._df = df
        self._connection = connection
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):
        columns = list(self._df.columns)
        format_columns = [item.lower().replace(' ', '_') for item in columns]
        columns_string = ', '.join(format_columns)
        primary_key = format_columns[0]

        self.query = f"""
        INSERT INTO public.{self._prefact}(
        {columns_string})
        VALUES ({('%s,'*len(columns))[:-1]})
        ON CONFLICT ({primary_key}) DO NOTHING;
        """


    def insert_data(self):
        try:
            conn = self.conn
            cursor = conn.cursor()

            for index, row in self._df.iterrows():
                data =[row[col] for col in self._df.columns]
                cursor.execute(self.query, data)
            conn.commit()
            print(f'\n\t{index+1} rows inserted')

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data insertion: {e}")

        finally:
            if cursor:
                cursor.close()

class MergeQueriesManager:
    def __init__(self,df: pd.DataFrame, connection: PgConnecionManager, prefact_table: str ,fact_table: str):
        self._df = df
        self._connection = connection
        self._fact = fact_table
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):

        columns = list(self._df.columns)
        format_columns = [item.lower().replace(' ', '_') for item in columns]
        primary_key = format_columns[0]

        update_set = ", ".join([f"{col}=src.{col}" for col in format_columns])

        insert_columns = ", ".join(format_columns)
        insert_values = ", ".join([f"src.{col}" for col in format_columns])

        self.query = f"""
        MERGE INTO {self._fact} AS lve
        USING {self._prefact} AS src
        ON lve.{primary_key} = src.{primary_key}

        WHEN MATCHED THEN
            UPDATE SET 
            {update_set}

        WHEN NOT MATCHED THEN
            INSERT ({insert_columns})
            VALUES ({insert_values});
        """

    def merge_data(self):
    
        try:
            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(self.query)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data merge: {e}")

        finally:
            if cursor:
                cursor.close()

class QueriesManager:
    def __init__(self, df:pd.DataFrame, connection:PgConnecionManager, prefact_table:str, fact_table:str):
        self._truncateManager = TruncateQueriesManager(connection, prefact_table)
        self._insertManager = InsertQueriesManager(df, connection, prefact_table)
        self._mergeManager = MergeQueriesManager(df, connection, prefact_table,fact_table)

    def truncate_data(self):
        self._truncateManager.truncate_table()

    def insert_data(self):
        self._insertManager.insert_data()

    def merge_data(self):
        self._mergeManager.merge_data()

    def process_data(self):
        self.truncate_data()
        self.insert_data()
        self.merge_data()
            

    ###########################################
    ########### API extraction ################
    ###########################################

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