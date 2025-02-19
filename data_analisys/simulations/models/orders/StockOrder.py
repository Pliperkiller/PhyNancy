from datetime import datetime
from typing import Optional
from ..buyers import StockBuyer
from .Order import Order

class StockOrder(Order):
    def __init__(self, buyer: StockBuyer):
        super().__init__(buyer)
        self.trade_commission: float = None
        self.stop_loss: Optional[float] = None
        self.take_profit: Optional[float] = None

    def open(self, price: float, value: float, open_date: Optional[datetime] = None, 
             stop_loss: Optional[float] = None, take_profit: Optional[float] = None):
        """
        Opens a stock order
        
        Args:
            price: Entry price
            value: Investment value
            open_date: Opening date
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
        """
        self.trade_commission = self.buyer.trade_commission
        self.open_price = price
        self.open_value = value
        self.position_size = value * (1 - self.trade_commission)  # Real value after commissions
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.is_open = True
        self.open_date = open_date or datetime.now()
        self.update_status('open')
        
        print(f'Open Stock Order {self.id} at price {self.open_price} for {self.open_value} USDT on {self.open_date}')
        if stop_loss:
            print(f'Stop Loss set at {self.stop_loss}')
        if take_profit:
            print(f'Take Profit set at {self.take_profit}')

    def close(self, price: float, close_date: Optional[datetime] = None):
        """
        Closes a stock order
        
        Args:
            price: Closing price
            close_date: Closing date
        """
        self.close_price = price
        self.trade_rate = self.close_price / self.open_price
        
        # Calculate the closing value considering entry and exit commissions
        self.close_value = self.position_size * self.trade_rate * (1 - self.trade_commission)
        self.value_change = self.close_value - self.open_value
        self.profit_loss = self.value_change  # Update the final P&L
        
        self.is_open = False
        self.close_date = close_date or datetime.now()
        self.update_status('closed')
        
        print(f'Close Stock Order {self.id} at price {self.close_price} for {self.close_value:.2f} USDT on {self.close_date}')
        print(f'P&L: {self.profit_loss:.2f} USDT ({(self.trade_rate - 1) * 100:.2f}%)')

    def _calculate_profit_loss(self, current_price: float) -> float:
        """
        Calculates the current P&L of the order
        
        Args:
            current_price: Current market price
            
        Returns:
            float: Current P&L in USDT
        """
        if not self.is_open:
            return self.profit_loss or 0.0
        
        current_rate = current_price / self.open_price
        current_value = self.position_size * current_rate * (1 - self.trade_commission)
        return current_value - self.open_value

    def _evaluate_close_conditions(self, current_price: float, high_price: float, low_price: float) -> bool:
        """
        Evaluates if the order should be closed based on current conditions
        
        Args:
            current_price: Current price
            high_price: Highest price of the period
            low_price: Lowest price of the period
            
        Returns:
            bool: True if the order should be closed
        """
        if not self.is_open:
            return False
            
        # Check stop loss
        if self.stop_loss and low_price <= self.stop_loss:
            self.close_price = self.stop_loss  # Prepare the closing price
            return True
            
        # Check take profit
        if self.take_profit and high_price >= self.take_profit:
            self.close_price = self.take_profit  # Prepare the closing price
            return True
            
        return False

    def to_dict(self) -> dict:
        """
        Converts the order to a dictionary, including StockOrder specific fields
        
        Returns:
            dict: Dictionary with all order fields
        """
        base_dict = super().to_dict()
        stock_specific = {
            'trade_commission': self.trade_commission,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
        }
        return {**base_dict, **stock_specific}
