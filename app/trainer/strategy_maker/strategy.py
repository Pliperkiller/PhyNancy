import pandas_ta as ta
import pandas as pd
import numpy as np

def EMADX_strategy(data,fast_EMA=9,slow_EMA=21, long_EMA = 200 ,ADX_thresh=25,ADX_period=14):
    """
    This function receives a DataFrame with historical data (containing the columns 'High', 'Low', and 'Close'), calculates two EMAs and the ADX, and determines the trend for each candle.

    The rule is:

    - If the fast EMA > slow EMA and ADX > ADX_thresh ⇒ buy signal.
    - If the fast EMA < slow EMA and ADX > ADX_thresh ⇒ sell signal.
    - Otherwise, no signal.
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
    
    df['Signal'] = np.where(
        (df['EMA_fast'] > df['EMA_slow']) & (df['ADX'] > ADX_thresh) & (df['EMA_fast'] > df['EMA_long']) & (df['EMA_slow'] > df['EMA_long']), 1,#buy signal
        np.where(
            (df['EMA_fast'] < df['EMA_slow']) & (df['ADX'] > ADX_thresh) & (df['EMA_fast'] < df['EMA_long']) &(df['EMA_slow'] < df['EMA_long']), -1,#sell signal
            0
        )
    )
    
    
    return df