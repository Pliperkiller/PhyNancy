import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'

class BasicBuyer:
    def __init__(self,funds=100):
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
        pass

    def recalculate_params(self):
        if self._buy_price:
            trade_rate = (self._sell_price/self._buy_price)
            self.funds = trade_rate * self.funds

            self.calculate_trade_rate(trade_rate)
            self.calculate_drawdowun()
            self.calculate_winstreak()
            self.reset_status()

        pass

    def buy(self,buy_price):
        if not self.buy_status:
            self._buy_price = buy_price
            self.buy_status = True
        pass

    def sell(self, sell_price):
        if self.buy_status:
            self._sell_price = sell_price

            self.check_result()
            self.recalculate_params()
        pass

    def check_result(self):
        if self._buy_price < self._sell_price:
            self.win_count+=1
        else:
            self.lose_count+=1
        pass

    def calculate_drawdowun(self):
        self.max_drawdown = min(self.funds,self.max_drawdown)
        pass

    def calculate_winstreak(self):
        if self._buy_price > self._sell_price:
            self._winstreak+=1
            self._losestreak = 0
            self.max_winstreak = max(self.max_winstreak, self._winstreak)
        else:
            self._losestreak+=1
            self._winstreak = 0
            self.max_losestreak = max(self.max_losestreak,self._losestreak)
        pass

    def calculate_trade_rate(self,trade_rate):
        self.max_trade_rate = max(self.max_trade_rate,trade_rate)
        self.min_trade_rate = min(self.min_trade_rate,trade_rate)
        pass

    def reset_status(self):
        self._buy_price = 0
        self._sell_price = 0
        self.buy_status = False



class StrategyManager:
    def __init__(self,initial_trend,fig = None):
        self.buyer = BasicBuyer()
        self.trend = None
        self.read_trend(initial_trend)
        self.total_purchases = 0
        self.fig = fig
        pass

    def read_trend(self,trend):
        self.trend = trend

    def check_strategy(self,trend,price,time):
        self.read_trend(trend)
        if (not self.buyer.buy_status) and (self.trend == 'uptrend'):
            self.total_purchases += 1
            self.buyer.buy(buy_price=price)
            if self.fig:
                self.fig.add_hline(y=price, line=dict(color="green", width=2, dash="dash"))
                self.fig.add_vline(x=time, line=dict(color="green", width=2, dash="dash"))

        if (self.buyer.buy_status) and (self.trend == 'downtrend'):
            self.buyer.sell(sell_price=price)
            if self.fig:
                self.fig.add_hline(y=price, line=dict(color="red", width=2, dash="dash"))
                self.fig.add_vline(x=time, line=dict(color="red", width=2, dash="dash"))
        pass

    def report_funds(self):
        return self.buyer.funds
    
    def print_stats(self):
        print(f'Final funds: {self.buyer.funds}',
              f'Total trades: {self.total_purchases}',
              f'Win trades: {self.buyer.win_count}',
              f'Lose trades: {self.buyer.lose_count}',
              f'Max trade rate: {self.buyer.max_trade_rate}',
              f'Min trade rate: {self.buyer.min_trade_rate}',
              f'Max win streak: {self.buyer.max_winstreak}',
              f'Max lose streak: {self.buyer.max_losestreak}',
              f'Max drawdown: {self.buyer.max_drawdown}',
              sep='\n')
        

def plot_strategy():
    i = 0
    fig = px.scatter(filtered_df, x="open_time", y="open", color="EMADX_trend", title="Scatterplot de Open Price vs Open Time")
    fig.update_layout(xaxis_title="Open Time", yaxis_title="Open Price",height=1000)
    for index, row in filtered_df.iterrows():
        if i == 0: 
            strategy = StrategyManager(initial_trend=row['EMADX_trend'],fig=fig)
        strategy.check_strategy(trend=row['EMADX_trend'],price=row['open'],time=row['open_time'])

        i+=1
    print(f'Win: {strategy.buyer.win_count}',f'Loose: {strategy.buyer.lose_count}',sep='\n')

    fig.show()

def check_strategy(df):
    i = 0
    funds = []
    for index, row in df.iterrows():
        if i == 0: 
            strategy = StrategyManager(initial_trend=row['EMADX_trend'])
        strategy.check_strategy(trend=row['EMADX_trend'],price=row['close'],time=row['open_time'])
        funds += [strategy.report_funds()]
        

        i+=1
    strategy.print_stats()
    return funds

def strategy_sumary(funds,time):
    Y = funds
    X = list(time)

    # Crear el line plot
    plt.plot(X, Y, label="Funds vs Time", color='b')  # Puedes cambiar el color si lo deseas

    # Etiquetas y título
    plt.xlabel('Time')  # Etiqueta del eje X
    plt.ylabel('Funds')  # Etiqueta del eje Y
    plt.title("Funds vs Time")  # Título del gráfico

    # Mostrar la leyenda
    plt.legend()

    # Mostrar la figura
    plt.show()

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

def plot_strategy_signals(df):
    color_map = {
        "downtrend": "red",
        "uptrend": "green",
        "sideways": "#ADD8E6"
    }
    fig = px.scatter(df, 
                    x="open_time", 
                    y="close", 
                    color="EMADX_trend", 
                    title="Scatterplot de Open Price vs Open Time", 
                    color_discrete_map=color_map)
    fig.update_layout(xaxis_title="Open Time", yaxis_title="Open Price",height=1000)

    fig.add_trace(go.Scatter(
        x=df["open_time"], 
        y=df["EMA_fast"], 
        mode='lines', 
        name='EMA_fast',
        line=dict(color='orange', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df["open_time"], 
        y=df["EMA_slow"], 
        mode='lines', 
        name='EMA_slow',
        line=dict(color='purple', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df["open_time"], 
        y=df["EMA_long"], 
        mode='lines', 
        name='EMA_long',
        line=dict(color='blue', width=2)
    ))

    # Mostrar la gráfica
    fig.show()