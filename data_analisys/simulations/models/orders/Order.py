from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Literal
# from ..buyers import Buyer

class Order(ABC):
    _id_counter = 0

    def __init__(self, buyer):
        self.id = Order._id_counter
        Order._id_counter += 1
        self.buyer: Buyer = buyer
        
        # Variables comunes
        self.open_price: Optional[float] = None
        self.close_price: Optional[float] = None
        self.open_value: Optional[float] = None
        self.close_value: Optional[float] = None
        self.is_open: bool = False
        self.value_change: Optional[float] = None
        self.trade_rate: Optional[float] = None
        self.open_date: Optional[datetime] = None
        self.close_date: Optional[datetime] = None
        
        # Nuevas variables
        self.status: Literal['pending', 'open', 'closed', 'cancelled'] = 'pending'
        self.last_update_date: Optional[datetime] = None
        self.profit_loss: Optional[float] = None
        self.position_size: Optional[float] = None

    @abstractmethod
    def open(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        pass
    
    def update_status(self, new_status: Literal['pending', 'open', 'closed', 'cancelled']):
        """Updates the order status and logs the update date"""
        self.status = new_status
        self.last_update_date = datetime.now()
    
    def calculate_current_profit_loss(self, current_price: float) -> float:
        """Calculates the current P&L of the order based on the current price"""
        if not self.is_open:
            return 0.0
        return self._calculate_profit_loss(current_price)
    
    @abstractmethod
    def _calculate_profit_loss(self, current_price: float) -> float:
        """Abstract method to calculate P&L specific to each type of order"""
        pass
    
    def should_close(self, current_price: float, high_price: float, low_price: float) -> bool:
        """Determines if the order should be closed based on current conditions"""
        if not self.is_open:
            return False
        return self._evaluate_close_conditions(current_price, high_price, low_price)
    
    @abstractmethod
    def _evaluate_close_conditions(self, current_price: float, high_price: float, low_price: float) -> bool:
        """Abstract method to evaluate close conditions specific to each type of order"""
        pass
    
    def cancel(self):
        """Cancels the order if it is pending"""
        if self.status == 'pending':
            self.update_status('cancelled')
            print(f'Order {self.id} cancelled')
    
    def to_dict(self) -> dict:
        """Converts the order to a dictionary for storage or logging"""
        return {
            'id': self.id,
            'status': self.status,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'open_value': self.open_value,
            'close_value': self.close_value,
            'is_open': self.is_open,
            'value_change': self.value_change,
            'trade_rate': self.trade_rate,
            'open_date': self.open_date,
            'close_date': self.close_date,
            'last_update_date': self.last_update_date,
            'profit_loss': self.profit_loss,
            'position_size': self.position_size
        }

