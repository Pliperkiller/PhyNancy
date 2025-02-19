from typing import Optional, Tuple
from ..orders.Order import Order
from ..orders.StockOrder import StockOrder
from .Buyer import Buyer


class StockBuyer(Buyer):
    """Implementation of Buyer for the stock market"""
    def __init__(self, trade_commission: float, trade_value: float):
        super().__init__(trade_value)
        self.trade_commission = trade_commission

    def manage_signal(self) -> None:
        """Manages signals for the stock market"""
        if not self.current_candle:
            return

        if self.current_candle.signal == 1 and not self.in_order:
            self.open_order()
        elif self.current_candle.signal == -1 and self.in_order:
            for order in self.get_active_orders():
                self.close_order(order)

    def open_order(self) -> None:
        """Opens a stock purchase order"""
        if not self.current_candle:
            return

        order = StockOrder(buyer=self)
        order.open(
            price=self.current_candle.close,
            value=self.trade_value,
            open_date=self.current_candle.timestamp,
            stop_loss=self.current_candle.stop_loss,
            take_profit=self.current_candle.take_profit
        )
        self.orders.append(order)
        self.in_order = True

    def close_order(self, order: Order) -> None:
        """
        Closes a stock order
        
        Args:
            order: Order to close
        """
        if not self.current_candle:
            return

        order.close(
            price=self.current_candle.close,
            close_date=self.current_candle.timestamp
        )
        
        # Register order in the history
        self.order_history.append(order.to_dict())
        self.in_order = False