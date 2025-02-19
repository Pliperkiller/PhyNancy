from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
from ..orders.Order import Order
from ..candles.Candle import Candle

class Buyer(ABC):
    """
    Abstract base class for market buyers.
    Manages market reading and order handling.
    """
    def __init__(self, trade_value: float):
        self.orders: List[Order] = []
        self.trade_value: float = trade_value
        self.current_candle: Optional[Candle] = None
        self.in_order: Optional[bool] = False
        
        # History for analysis
        self.order_history: List[Dict] = []
        self.market_history: List[Candle] = []

    def read_chart(self, candle: Candle) -> None:
        """
        Reads and processes a new market candle
        
        Args:
            candle: Candle with market information
        """
        self.current_candle = candle
        self.market_history.append(candle)
        self.manage_orders()
        self.manage_signal()

    @abstractmethod
    def manage_signal(self) -> None:
        """Manages trading signals according to the specific strategy"""
        pass

    def manage_orders(self) -> None:
        """
        Manages open orders, checking closing conditions
        and updating take profit/stop loss if necessary
        """
        if not self.orders:
            return

        for order in self.orders:
            if not order.is_open:
                continue

            # Check if the order should be closed
            if self.should_close_order(order):
                self.close_order(order)

    def should_close_order(self, order: Order) -> bool:
        """
        Determines if an order should be closed based on current conditions
        
        Args:
            order: Order to evaluate
            
        Returns:
            bool: True if the order should be closed
        """
        if not self.current_candle:
            return False

        return order._evaluate_close_conditions(
            current_price=self.current_candle.close,
            high_price=self.current_candle.high,
            low_price=self.current_candle.low
        )

    @abstractmethod
    def open_order(self) -> None:
        """Opens a new order according to the specific strategy"""
        pass

    @abstractmethod
    def close_order(self, order: Order) -> None:
        """
        Closes a specific order
        
        Args:
            order: Order to close
        """
        pass

    def get_active_orders(self) -> List[Order]:
        """
        Gets the currently open orders
        
        Returns:
            List[Order]: List of open orders
        """
        return [order for order in self.orders if order.is_open]

    def get_order_stats(self) -> Dict:
        """
        Gets statistics of the executed orders
        
        Returns:
            Dict: Trading statistics
        """
        total_orders = len(self.order_history)
        if total_orders == 0:
            return {"message": "No orders to analyze"}

        winning_orders = len([order for order in self.order_history if order['profit_loss'] > 0])
        
        return {
            "total_orders": total_orders,
            "winning_orders": winning_orders,
            "win_rate": winning_orders / total_orders * 100,
            "total_profit_loss": sum(order['profit_loss'] for order in self.order_history)
        }