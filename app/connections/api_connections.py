
from abc import ABC, abstractmethod
import binance.client as bclient

# Responsible for generating connectors for API services by using the api keys obtained from the keys.json files inside the folder keys

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