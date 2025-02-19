from typing import Optional, Tuple
from ..orders.Order import Order
from ..orders.FuturesOrder import FuturesOrder
from .Buyer import Buyer


class FuturesBuyer(Buyer):
    """Implementation of Buyer for the stock market"""
    def __init__(self,margin: float,leverage: float, taker_commission: float, maker_commission: float):
        super().__init__(trade_value=margin)
        self.margin = margin
        self.leverage = leverage
        self.taker_commission = taker_commission
        self.maker_commission = maker_commission

    def manage_signal(self) -> None:
        """
        Manages signals for the stock market.
        
        This method checks the current candle for trading signals. If the signal is 1 (buy) 
        or -1 (sell), it triggers the opening of a new order.
        """
        if not self.current_candle:
            return

        if self.current_candle.signal == 1 or self.current_candle.signal == -1:
            self.open_order()


    def open_order(self) -> None:
        """Opens a stock purchase order"""
        if not self.current_candle:
            return

        order = FuturesOrder(buyer=self)
        order_type = 'Long' if self.current_candle.signal == 1 else 'Short'
        order.open(
            price=self.current_candle.close,
            value=self.margin,
            leverage=self.leverage,
            order_type= order_type,
            open_date=self.current_candle.timestamp,
            stop_loss=self.current_candle.stop_loss,
            take_profit=self.current_candle.take_profit
        )
        self.orders.append(order)


    def close_order(self, order: FuturesOrder) -> None:
        """
        Closes a stock order
        
        Args:
            order: Order to close
        """
        if not self.current_candle:
            return

        order.close(
            high_price=self.current_candle.high,
            low_price=self.current_candle.low,
            close_price=self.current_candle.close,
            close_date= self.current_candle.timestamp
        )
        
        # Register order in the history
        self.order_history.append(order.to_dict())
