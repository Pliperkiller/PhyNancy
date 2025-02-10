import pandas_ta as ta
import pandas as pd

def EMADX_strategy(data,fast_EMA=9,slow_EMA=21, long_EMA = 200 ,ADX_thresh=25,ADX_period=14):
    """
    This function receives a DataFrame with historical data (containing the columns 'High', 'Low', and 'Close'), calculates two EMAs and the ADX, and determines the trend for each candle.

    The rule is:

    - If the fast EMA > slow EMA and ADX > ADX_thresh ⇒ Uptrend.
    - If the fast EMA < slow EMA and ADX > ADX_thresh ⇒ Downtrend.
    - Otherwise, the market is considered to be in a sideways range.
    """
    df = data.copy()
    #EMA CALC default is 9 for fast and 21 for slow
    df['EMA_fast'] = ta.ema(df['close'], length=fast_EMA)
    df['EMA_slow'] = ta.ema(df['close'], length=slow_EMA)
    df['EMA_long'] = ta.ema(df['close'], length=long_EMA)
    
    # ADX
    adx_df = ta.adx(high=df['high'], low=df['low'], close=df['close'])
    colname = 'ADX_'+str(ADX_period)
    df['ADX'] = adx_df[colname]
    
    # Función para determinar la tendencia según las condiciones definidas.
    def trend_signal(row):
        if pd.isna(row['EMA_fast']) or pd.isna(row['EMA_slow']) or pd.isna(row['ADX']):
            return 'undefined'
        if row['EMA_fast'] > row['EMA_slow'] and row['ADX'] > ADX_thresh and row['EMA_fast']> row['EMA_long'] and row['EMA_slow'] > row['EMA_long']:
            return 'uptrend'
        elif row['EMA_fast'] < row['EMA_slow'] and row['ADX'] > ADX_thresh and row['EMA_fast']<row['EMA_long'] and row['EMA_slow']<row['EMA_long']:
            return 'downtrend'
        else:
            return 'sideways'
    
    df['EMADX_trend'] = df.apply(trend_signal, axis=1)
    
    return df

