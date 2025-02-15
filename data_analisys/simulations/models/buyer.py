from abc import ABC, abstractmethod

class Buyer(ABC):
    @abstractmethod
    def create_order(self):
        pass

class StockBuyer(Buyer):
    def create_order(self):
        print('Create Stock Order')