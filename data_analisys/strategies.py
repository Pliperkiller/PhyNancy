import pandas_ta as ta
import pandas as pd
import numpy as np  

def HOLD_strategy(data):
    """
    This function receives a DataFrame with historical data and returns a DataFrame with a 'signal' column that is always 0, meaning that the strategy is to hold the asset.
    """
    df = data.copy()
    df['signal'] = 0
    df.loc[0,'signal']=1
    df.loc[df.tail(1).index[0],'signal']=-1

    return df

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
    
    df['signal'] = np.where((df['EMA_fast'] > df['EMA_slow']) & (df['ADX'] > ADX_thresh) & (df['EMA_fast']> df['EMA_long']) & (df['EMA_slow'] > df['EMA_long']), 1, 
                    np.where((df['EMA_fast'] < df['EMA_slow']) & (df['ADX'] > ADX_thresh) & (df['EMA_fast']<df['EMA_long']) & (df['EMA_slow']<df['EMA_long']), -1, 
                                0))
    
    return df



def VOLUMEMADX_strategy(data, fast_EMA=9, slow_EMA=21, long_EMA=200, ADX_thresh=25, ADX_period=14, vol_sma_period=20):
    """
    Optimized EMADX Strategy with Volume Confirmation.

    Signals:
    - Buy: Fast EMA > Slow EMA > Long EMA, ADX > Threshold, Volume > SMA(Volume)
    - Sell: Fast EMA < Slow EMA < Long EMA, ADX > Threshold, Volume > SMA(Volume)
    """
    df = data.copy()

    # Calculate EMAs using pandas_ta
    df['EMA_fast'] = ta.ema(df['close'], length=fast_EMA)
    df['EMA_slow'] = ta.ema(df['close'], length=slow_EMA)
    df['EMA_long'] = ta.ema(df['close'], length=long_EMA)

    # ADX Calculation
    df['ADX'] = ta.adx(high=df['high'], low=df['low'], close=df['close'], length=ADX_period)['ADX_14']

    # Volume Confirmation
    df['Volume_SMA'] = df['volume'].rolling(window=vol_sma_period).mean()

    # Conditions
    buy = (
        (df['EMA_fast'] > df['EMA_slow']) &
        (df['EMA_slow'] > df['EMA_long']) &
        (df['ADX'] > ADX_thresh) &
        (df['volume'] > df['Volume_SMA'])
    )
    sell = (
        (df['EMA_fast'] < df['EMA_slow']) &
        (df['EMA_slow'] < df['EMA_long']) &
        (df['ADX'] > ADX_thresh) &
        (df['volume'] > df['Volume_SMA'])
    )

    # Generate Signals
    df['signal'] = np.select([buy, sell], [1, -1], default=0)

    return df

