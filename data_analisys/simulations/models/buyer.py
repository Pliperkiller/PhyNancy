from abc import ABC, abstractmethod
from order import StockOrder,BasicFuturesOrder,Order

class Buyer(ABC):
    def __init__(self,trade_value):
        self.trade_value = trade_value
        self.orders: list[Order] = []
        self.market_price = None
        self.signal = None

    @abstractmethod
    def open_order(self):
        pass

    @abstractmethod
    def close_orders(self):
        pass

class StockBuyer(Buyer):
    def __init__(self,trade_comission, trade_value):
        super().__init__(trade_value)
        self.trade_commission = trade_comission
        self.in_order = False

    def read_market_price(self,price):
        self.market_price = price
        pass

    def read_signal(self,signal):
        self.signal = signal
        pass

    def open_order(self):
        order = StockOrder(buyer=self)
        order.open(price=self.market_price, value= self.trade_value)
        self.orders.append(order)
        self.in_order=True
        pass

    def close_orders(self):
        for order in self.orders:
            if order.is_open:
                order.close(price=self.market_price)
        self.in_order = False
        pass

    def read_chart(self,price,signal):
        self.read_market_price(price)
        self.read_signal(signal)
        pass

    def manage_signal(self):
        if self.signal ==1 and not self.in_order:
            self.open_order()
        elif self.signal ==-1 and self.in_order:
            self.close_orders()
            