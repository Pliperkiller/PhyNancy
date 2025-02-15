from abc import ABC, abstractmethod

class Order(ABC):
    @abstractmethod
    def open(self):
        pass
    @abstractmethod
    def close(self): 
        pass

class StockOrder:
    _id_counter = 0

    def __init__(self, buyer):
        """
        price es el precio de la acción.
        value es la cantidad de dinero que el comprador está dispuesto a gastar.
        """
        self.id = StockOrder._id_counter
        StockOrder._id_counter += 1

        self.buyer = buyer
        self.open_price = None
        self.close_price = None
        self.open_value = None
        self.close_value = None
        self.open_status = False
        self.trade_comission = None
        self.trade_rate = None
        self.value_change = None

    def open(self, price, value):
        self.trade_comission = self.buyer.trade_comission
        self.open_price = price
        self.open_value = value
        self.open_status = True
        print(f'Open Stock Order {self.id} at price {self.open_price} for {self.open_value} USDT')

    def close(self, price):
        if not self.open_status:
            print(f'Error: Order {self.id} is not open.')
            return

        self.close_price = price
        self.trade_rate = self.close_price / self.open_price
        self.close_value = self.open_value * self.trade_rate * (1 - self.trade_comission) ** 2
        self.value_change = self.close_value - self.open_value

        print(f'Close Stock Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT')


class FuturesOrder(Order):

    def open(self):
        print('Open Futures Order')
    def close(self):
        print('Close Futures Order')