from abc import ABC, abstractmethod
from buyer import Buyer, StockBuyer
# TODO: Add order open date att,
# TODO: Manage TP and SL with max and min cases (cases when TP and SL collide with candlestick max or min)
class Order(ABC):
    _id_counter = 0

    def __init__(self, buyer):
        self.id = Order._id_counter
        Order._id_counter += 1
        self.buyer: Buyer = buyer
        
        # Variables comunes
        self.open_price = None
        self.close_price = None
        self.open_value = None
        self.close_value = None
        self.is_open = False
        self.value_change = None
        self.trade_rate = None

    @abstractmethod
    def open(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, price):
        pass

class StockOrder(Order):
    def __init__(self, buyer: StockBuyer):
        super().__init__(buyer)
        self.trade_commission = None

    def open(self, price, value):
        self.trade_commission = self.buyer.trade_commission
        self.open_price = price
        self.open_value = value
        self.is_open = True
        print(f'Open Stock Order {self.id} at price {self.open_price} for {self.open_value} USDT')

    def close(self, price):
        self.close_price = price
        self.trade_rate = self.close_price / self.open_price
        self.close_value = self.open_value * self.trade_rate * (1 - self.trade_commission) ** 2
        self.value_change = self.close_value - self.open_value
        self.is_open = False
        print(f'Close Stock Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT')

class BasicFuturesOrder(Order):
    def __init__(self, buyer):
        super().__init__(buyer)
        self.taker_commission = None
        self.maker_commission = None
        self.leverage = None
        self.position_size = None
        self.stop_loss = None
        self.take_profit = None
        self.rr_ratio = None
        self.order_type = None

    def open(self, price, value, leverage, rr_ratio, stop_loss, order_type):
        self.taker_commission = self.buyer.taker_commission
        self.maker_commission = self.buyer.maker_commission
        self.open_price = price
        self.open_value = value
        self.is_open = True
        self.leverage = leverage
        self.position_size = value * self.leverage
        self.rr_ratio = rr_ratio
        self.stop_loss = stop_loss
        self.order_type = order_type

        if self.order_type == 'Long':
            risk_range = self.open_price - self.stop_loss
            self.take_profit = self.open_price + risk_range * self.rr_ratio
        elif self.order_type == 'Short':
            risk_range = self.stop_loss - self.open_price
            self.take_profit = self.open_price - risk_range * self.rr_ratio

        print(f'Open {self.order_type} Order {self.id} at price {self.open_price}, take profit {self.take_profit} and stop loss {self.stop_loss} for {self.open_value} USDT')

    def close(self, price):
        tp = self.take_profit
        sl = self.stop_loss

        if self.order_type == 'Long':
            self.close_price = tp if tp < price else (sl if sl > price else price)
            rate = self.close_price / self.open_price
            self.close_value = self.open_value + self.position_size * (rate - 1) - self.position_size * (self.taker_commission + rate * self.maker_commission)
            self.trade_rate = rate

        elif self.order_type == 'Short':
            self.close_price = sl if sl < price else (tp if tp > price else price)
            rate = self.close_price / self.open_price
            self.close_value = self.open_value + self.position_size * (1 - rate) - self.position_size * (self.taker_commission + rate * self.maker_commission)
            self.trade_rate = 1 / rate

        self.value_change = self.close_value - self.open_value
        self.is_open = False
        print(f'Close {self.order_type} Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT')

