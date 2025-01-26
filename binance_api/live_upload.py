from futures_tools import *
from datetime import datetime

if __name__=='__main__':

    ###########################################
    ########### CREDENTIALS ###################
    ###########################################

    #keys location:
    file_name = 'keys.json'
    folder_name = 'keys'
    json_path = read_folder_file(folder_name, file_name)

    #pg credentials
    pg_service_name = "pgcurrencies"
    credentials = get_credentials(pg_service_name,json_path)

    #binance futures credentials
    binance_service_name = "FuturesTestnet"
    keys = get_credentials(binance_service_name,json_path)
    api_key = keys['api_key']
    api_secret = keys['api_secret']

    ###########################################
    ########### CONNECTIONS ###################
    ###########################################

    # pgsql connection
    conn = psycopg2.connect(
        host=credentials['hostname'],
        database=credentials['database'],
        port=credentials['port'],
        user=credentials['username'],
        password=credentials['password']
    )
    cursor = conn.cursor()

    # Binance client connection
    client = Client(api_key, api_secret,testnet=True)


    ###########################################
    ########### RUNTIME #######################
    ###########################################

    # Table name
    source_table_name = 'btcusdtfutures_source'
    live_table_name = 'btcusdtfutures_live'
    # Currency params
    symbol = 'BTCUSDT'  # trading currency
    interval = Client.KLINE_INTERVAL_5MINUTE  # time interval
    limit = 300  # max limit
    
    #Data streaming loop
    try:
        while True:
            print("===============================",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            #Truncate source table
            truncate_table(source_table_name,conn,cursor)

            #Extract data from api
            last_candles = get_last_candles(symbol,limit,interval,client)
            
            #Insert data into source
            counter = 0
            for index, row in last_candles.iterrows():
                candle =(
                    row['Open Time'], row['Open'], row['High'], 
                    row['Low'], row['Close'],row['Volume'], 
                    row['Close Time'], row['Quote Asset Volume'],
                    row['Number of Trades'], row['Taker Buy Base Volume'],
                    row['Taker Buy Quote Volume'], row['Ignore']
                    )
                insert_to_db(candle,conn,cursor,source_table_name)

            merge_tables(source_table_name,live_table_name,conn,cursor)
            
            print(f"Updated ")
            # wait 1 minute for next update
            time.sleep(250)

    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()