import psycopg2
from credential_manager import *
import binance.client as bclient

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