from stream import binance_stream_reader as bsr
import websocket


# Example of using the BinanceWebSocket class

def handle_kline_update(is_closed, open_price, high_price, low_price, close_price, volume):
    """Function that handles the candle data when updated"""
    
    if is_closed:
        print(f"\nActual candle updated:\n Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}", end='\r')


if __name__ == "__main__":

    # Create an instance for the BTC/USDT pair and 15-minute candles
    ws = bsr.BinanceFuturesWebSocket(symbol="btcusdt", interval="15m", on_kline_update=handle_kline_update)
    ws.start()
