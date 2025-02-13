from stream import binance_stream_reader as bsr
import websocket
from datetime import datetime
import pytz

# Example of using the BinanceWebSocket class

def handle_kline_update(is_closed, open_time, close_time, open_price, high_price, low_price, close_price, volume):
    """Function that handles the candle data when updated"""

    open_time_utc = datetime.utcfromtimestamp(open_time / 1000)
    close_time_utc = datetime.utcfromtimestamp(close_time / 1000)

    # Convert UTC time to local time
    local_tz = pytz.timezone('America/New_York')  # Change to your local timezone
    open_time_local = open_time_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
    close_time_local = close_time_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
    open_time_local_str = open_time_local.strftime('%Y-%m-%d %H:%M:%S')
    close_time_local_str = close_time_local.strftime('%Y-%m-%d %H:%M:%S')

    if is_closed:
        print(f"Open Time: {open_time_local_str}, Close Time: {close_time_local_str}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}", end='\r')
        with open("live_candle_data.csv", "w") as file:
            file.write("Open Time,Close Time,Open,High,Low,Close,Volume\n")
            file.write(f"{open_time_local_str},{close_time_local_str},{open_price},{high_price},{low_price},{close_price},{volume}\n")


if __name__ == "__main__":

    # Create an instance for the BTC/USDT pair and 15-minute candles
    ws = bsr.BinanceFuturesWebSocket(symbol="btcusdt", interval="15m", on_kline_update=handle_kline_update)
    ws.start()
