from futures_tools import *
from datetime import datetime, timedelta

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
    source_table_name = 'btcusdtfutures_historic'
    live_table_name = 'btcusdtfutures_live'
    # Currency params
    symbol = 'BTCUSDT'  # trading currency
    interval = Client.KLINE_INTERVAL_5MINUTE  # time interval
    
    start_date = '2025-01-25'
    stop_date = '2024-01-25'

    #Data streaming loop
    try:
        initial_date = start_date


        while initial_date != stop_date:
            end_date = (datetime.strptime(initial_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"Loading data: from {end_date} to {initial_date}")
            #Truncate source table
            truncate_table(source_table_name,conn,cursor)

            #Extract data from api
            last_candles = get_historic_candles(symbol,end_date,initial_date,interval, client)
            #Insert data into historic
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

            #Reload date
            initial_date = end_date
            print("\n")
            # wait 1 second for next update
            time.sleep(1)

    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()