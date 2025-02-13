from stream import binance_stream_reader as bsr
import websocket


# Example of using the BinanceWebSocket class

def handle_kline_update(is_closed, open_price, high_price, low_price, close_price, volume):
    """Function that handles the candle data when updated"""
    
    
    # You can add your logic here to make decisions based on price action
    if is_closed:
        print(f"\nActual candle updated:\n Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}", end='\r')
        with open("candle_data.txt", "a") as file:
            file.write(f"Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}\n")


if __name__ == "__main__":

    # Create an instance for the BTC/USDT pair and 15-minute candles
    ws = bsr.BinanceFuturesWebSocket(symbol="btcusdt", interval="1m", on_kline_update=handle_kline_update)
    ws.start()
