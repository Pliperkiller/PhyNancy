from abc import ABC, abstractmethod
import websocket
import json

class BinanceWebSocket(ABC):
    """Abstract class for Binance WebSocket clients"""
    def __init__(self, symbol: str, interval: str, on_kline_update):
        """
        Base constructor for any Binance WebSocket.

        :param symbol: Trading pair (e.g. 'btcusdt').
        :param interval: Kline interval (e.g. '15m', '1h', '5m').
        :param on_kline_update: Callback function to handle kline updates.
        """
        self.symbol = symbol.lower()
        self.interval = interval
        self.on_kline_update = on_kline_update
        self.socket = self.get_socket_url()

    @abstractmethod
    def get_socket_url(self) -> str:
        """Must be implemented in child classes to define the WebSocket URL"""
        pass

    def on_message(self, ws, message):
        """Processes messages received from the WebSocket"""
        data = json.loads(message)
        kline = data['k']

        # Extract kline data
        is_closed = kline['x']  # If the kline has closed
        open_price = float(kline['o'])
        high_price = float(kline['h'])
        low_price = float(kline['l'])
        close_price = float(kline['c'])
        volume = float(kline['v'])

        # Call the update function
        self.on_kline_update(is_closed, open_price, high_price, low_price, close_price, volume)

    def on_error(self, ws, error):
        """Error handling"""
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handles connection closure"""
        print("Connection closed")

    def on_open(self, ws):
        """Displays message when connection is opened"""
        print(f"Connected to Binance WebSocket for {self.symbol.upper()} on {self.interval}")

    def start(self):
        """Starts the WebSocket connection and keeps the stream running"""
        ws = websocket.WebSocketApp(self.socket, 
                                    on_message=self.on_message, 
                                    on_error=self.on_error, 
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()

class BinanceSpotWebSocket(BinanceWebSocket):
    """WebSocket for Binance spot market"""
    def get_socket_url(self) -> str:
        return f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_{self.interval}"

class BinanceFuturesWebSocket(BinanceWebSocket):
    """WebSocket for Binance futures market"""
    def get_socket_url(self) -> str:
        return f"wss://fstream.binance.com/ws/{self.symbol}@kline_{self.interval}"