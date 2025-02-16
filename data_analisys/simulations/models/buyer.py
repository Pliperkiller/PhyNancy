from abc import ABC, abstractmethod

class Buyer(ABC):
    @abstractmethod
    def create_order(self):
        pass

class StockBuyer(Buyer):
    def __init__(self,trade_comission, trade_value):
        self.trade_commision =trade_comission
        self.trade_value = trade_value
        



    def create_order(self):
        print('Create Stock Order')