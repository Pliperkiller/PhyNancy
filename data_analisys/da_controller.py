import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = 'browser'

class BasicBuyer:
    def __init__(self, funds=100):
        self.funds = funds
        self._buy_price = 0
        self._sell_price = 0
        self.win_count = 0
        self.lose_count = 0
        self.buy_status = False
        self.max_winstreak = 0
        self.max_losestreak = 0
        self._winstreak = 0
        self._losestreak = 0
        self.max_drawdown = funds
        self.max_trade_rate = 1
        self.min_trade_rate = 1

    def recalculate_params(self):
        if self._buy_price:
            trade_rate = self._sell_price / self._buy_price
            self.funds *= trade_rate

            self.calculate_trade_rate(trade_rate)
            self.calculate_drawdown()
            self.calculate_streaks()
            self.reset_status()

    def buy(self, buy_price):
        if not self.buy_status:
            self._buy_price = buy_price
            self.buy_status = True

    def sell(self, sell_price):
        if self.buy_status:
            self._sell_price = sell_price
            self.check_result()
            self.recalculate_params()

    def check_result(self):
        if self._buy_price < self._sell_price:
            self.win_count += 1
        else:
            self.lose_count += 1

    def calculate_drawdown(self):
        self.max_drawdown = min(self.funds, self.max_drawdown)

    def calculate_streaks(self):
        if self._sell_price > self._buy_price:  # Ganancia
            self._winstreak += 1
            self._losestreak = 0
            self.max_winstreak = max(self.max_winstreak, self._winstreak)
        else:  # Pérdida
            self._losestreak += 1
            self._winstreak = 0
            self.max_losestreak = max(self.max_losestreak, self._losestreak)

    def calculate_trade_rate(self, trade_rate):
        self.max_trade_rate = max(self.max_trade_rate, trade_rate)
        self.min_trade_rate = min(self.min_trade_rate, trade_rate)

    def reset_status(self):
        self._buy_price = 0
        self._sell_price = 0
        self.buy_status = False



class SpotTradeAnalyzer:
    def __init__(self, strategy_signals: pd.DataFrame, name: str='Strategy'):
        self.name = name
        self.data = strategy_signals
        self.buyer = BasicBuyer()
        self.total_trades = 0
        self.results ={}
        self.returns_chart = None
        self.check_strategy()
        self.set_results()

    def check_strategy(self):
        signals = self.data['signal'].values
        prices = self.data['close'].values
        funds = [0] * len(signals)
        times = self.data['open_time'].values

        buyer = self.buyer

        for i, (sig, price) in enumerate(zip(signals, prices)):

            if not buyer.buy_status and sig == 1 and isinstance(price, (int, float)):
                buyer.buy(price)
            elif buyer.buy_status and sig == -1 and isinstance(price, (int, float)) and not np.isnan(price):
                buyer.sell(price)
                self.total_trades += 1

            funds[i] = buyer.funds
        returns = pd.DataFrame({'open_time': times, 'funds': funds})
        returns['open_time'] = pd.to_datetime(returns['open_time'])
        self.returns_chart = returns
    
    def set_results(self):
        self.results['Final funds'] = self.buyer.funds
        self.results['Total trades'] = self.total_trades
        self.results['Win trades'] = self.buyer.win_count
        self.results['Lose trades'] = self.buyer.lose_count
        self.results['Max trade rate'] = self.buyer.max_trade_rate
        self.results['Min trade rate'] = self.buyer.min_trade_rate
        self.results['Max win streak'] = self.buyer.max_winstreak
        self.results['Max lose streak'] = self.buyer.max_losestreak
        self.results['Max drawdown'] = self.buyer.max_drawdown

    def print_results(self):
        for key, value in self.results.items():
            print(f'{key}: {value}')

    def plot_performance(self):
        df = self.returns_chart

        plt.figure(figsize=(14, 6))
        sns.lineplot(x='open_time', y='funds', data=df, label="Funds vs Time", color='b')

        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Agregar grids por cada mes
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.grid(which='minor', linestyle='--', linewidth=0.7, color='gray')
        ax.grid(which='major', linestyle='-', linewidth=1, color='black')

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.title(f'{self.name} Funds vs Time')
        plt.show()

    def plot_strategy_signals(self):
        df = self.data.copy()
        df['signal']=df['signal'].map({-1: 'Sell', 0: 'Hold', 1: 'Buy'})
        color_map = {
            "Sell": "red",
            "Buy": "green",
            "Hold": "#ADD8E6"
        }
        fig = px.scatter(df, 
                        x="open_time", 
                        y="close", 
                        color="signal", 
                        title="Scatterplot de Open Price vs Open Time", 
                        color_discrete_map=color_map)
        fig.update_layout(xaxis_title="Open Time", yaxis_title="Open Price")
        fig.show()

## GRAFICO DE VELAS

def plot_candlestick(data):
    
    fig = go.Figure(data=[go.Candlestick(
        x=data['open_time'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price')
    pio.show(fig, browser='default')

def format_df(df):
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
    df['number_of_trades'] = df['number_of_trades'].astype(int)
    df['taker_buy_base_volume'] = df['taker_buy_base_volume'].astype(float)
    df['taker_buy_quote_volume'] = df['taker_buy_quote_volume'].astype(float)
    df['ignore'] = df['ignore'].astype(int)
    return df

def detailed_backtest(df, strategy, **kwargs):
    strategy_df = strategy(df, **kwargs)
    trade_analyzer = SpotTradeAnalyzer(strategy_df,name=strategy.__name__)
    trade_analyzer.print_results()
    trade_analyzer.plot_performance()
    trade_analyzer.plot_strategy_signals()

def backtest(df, strategy, **kwargs):
    strategy_df = strategy(df, **kwargs)
    trade_analyzer = SpotTradeAnalyzer(strategy_df,name=strategy.__name__)
    return trade_analyzer.results['Final funds']