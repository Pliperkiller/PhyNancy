from abc import ABC, abstractmethod

class Order(ABC):
    _id_counter = 0

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

class StockOrder(Order):
    def __init__(self, buyer):
        """
        price: The price of the stock.
        value: The amount of money the buyer is willing to spend.
        """
        self.id = Order._id_counter
        Order._id_counter += 1

        self.buyer = buyer
        self.open_price = None
        self.close_price = None
        self.open_value = None
        self.close_value = None
        self.open_status = False
        self.trade_commission = None
        self.trade_rate = None
        self.value_change = None

    def open(self, price, value):
        self.trade_commission = self.buyer.trade_commission
        self.open_price = price
        self.open_value = value
        self.open_status = True
        print(f'Open Stock Order {self.id} at price {self.open_price} for {self.open_value} USDT')

    def close(self, price):
        self.close_price = price
        self.trade_rate = self.close_price / self.open_price
        self.close_value = self.open_value * self.trade_rate * (1 - self.trade_commission) ** 2
        self.value_change = self.close_value - self.open_value
        self.open_status = False
        print(f'Close Stock Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT')

class BasicFuturesOrder(Order):
    """
    price: The price of the stock.
    value: The amount of money the buyer is willing to spend.
    position_size: The size of the position = value * leverage.
    maker_commission: The commission for scheduled trades.
    taker_commission: The commission for immediate trades.
    """
    def __init__(self, buyer):
        self.id = Order._id_counter
        Order._id_counter += 1

        self.buyer = buyer
        self.open_price = None
        self.close_price = None
        self.open_value = None
        self.close_value = None
        self.open_status = False
        self.taker_commission = None
        self.maker_commission = None
        self.trade_rate = None
        self.position_size = None
        self.value_change = None
        self.leverage = None
        self.rr_ratio = None
        self.stop_loss = None
        self.take_profit = None
        self.order_type = None

    def open(self, price, value, leverage, rr_ratio, stop_loss, order_type):
        self.taker_commission = self.buyer.taker_commission
        self.maker_commission = self.buyer.maker_commission
        self.open_price = price
        self.open_value = value
        self.open_status = True
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
        self.close_price = price
        rate = self.close_price / self.open_price

        if self.order_type == 'Long':
            self.close_value = self.open_value + self.position_size * (rate - 1) - self.position_size * (self.taker_commission + rate * self.maker_commission)
            self.trade_rate = rate
        elif self.order_type == 'Short':
            self.close_value = self.open_value + self.position_size * (1 - rate) - self.position_size * (self.taker_commission + rate * self.maker_commission)
            self.trade_rate = 1/rate
        
        
        self.value_change = self.close_value - self.open_value
        self.open_status = False
        print(f'Close {self.order_type} Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT')
        
