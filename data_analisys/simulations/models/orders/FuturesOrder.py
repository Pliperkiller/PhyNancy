from abc import ABC, abstractmethod
from datetime import datetime
from operator import ne
from turtle import position
from typing import Optional, Literal
from .Order import Order
#TODO: Check calculations for final value and P&L
class FuturesOrder(Order):
    def __init__(self, buyer):
        super().__init__(buyer)
        self.taker_commission: Optional[float] = None
        self.maker_commission: Optional[float] = None
        self.leverage: Optional[float] = None
        self.position_size: Optional[float] = None
        self.stop_loss: Optional[float] = None
        self.take_profit: Optional[float] = None
        self.order_type: Optional[Literal['Long', 'Short']] = None
        self.liquidation_price: Optional[float] = None
        self.entry_commission: Optional[float] = None
        self.margin: Optional[float] = None

    def open(self, price: float, value: float, leverage: float, 
             stop_loss: float, order_type: Literal['Long', 'Short'], 
             open_date: datetime, take_profit: Optional[float] = None):
        """
        Abre una orden de futuros con opción de especificar take profit o usar rr_ratio
        
        Args:
            price: Precio de entrada
            value: Valor a invertir (margen)
            leverage: Apalancamiento
            stop_loss: Precio de stop loss
            order_type: Tipo de orden ('Long' o 'Short')
            open_date: Fecha de apertura
            take_profit: Precio de take profit (opcional)
            
        Raises:
            ValueError: Si no se proporciona ni take_profit ni rr_ratio
        """
            
        # Configuración básica
        self.taker_commission = self.buyer.taker_commission
        self.maker_commission = self.buyer.maker_commission
        self.entry_commission = self.taker_commission
        
        # Configuración de la posición
        self.open_price = price
        self.open_value = value
        self.margin = value
        self.leverage = leverage
        self.position_size = value * leverage
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.order_type = order_type
        self.open_date = open_date
        
        
        # Calcular precio de liquidación
        if self.order_type == 'Long':
            self.liquidation_price = self.open_price * (1 - (1 / self.leverage))
        else:
            self.liquidation_price = self.open_price * (1 + (1 / self.leverage))
        
        self.is_open = True
        self.update_status('open')
        
        self._print_order_details()


    def _print_order_details(self):
        """Imprime los detalles actualizados de la orden"""
        print(f'\n{self.order_type} Futures Order {self.id} Details:')
        print(f'  Entry Price: {self.open_price}')
        print(f'  Position Size: {self.position_size} USDT')
        print(f'  Leverage: {self.leverage}x')
        print(f'  Margin: {self.margin} USDT')

    def close(self, high_price: float, low_price: float, close_price: float, close_date: datetime):
        """
        Cierra una orden de futuros
        
        Args:
            high_price: Precio más alto del período
            low_price: Precio más bajo del período
            close_price: Precio de cierre actual
            close_date: Fecha de cierre
        """
        if not self.is_open:
            return

        # Determinar precio de cierre basado en condiciones
        if self.order_type == 'Long':
            if high_price >= self.take_profit:
                self.close_price = self.take_profit
            elif low_price <= self.stop_loss:
                self.close_price = self.stop_loss
            else:
                self.close_price = close_price
        else:  # Short
            if low_price <= self.take_profit:
                self.close_price = self.take_profit
            elif high_price >= self.stop_loss:
                self.close_price = self.stop_loss
            else:
                self.close_price = close_price

        # Cálculo de P&L y valores finales
        self._calculate_final_values()
        
        self.is_open = False
        self.close_date = close_date
        self.update_status('closed')
        
        print(f'Close {self.order_type} Futures Order {self.id}:')
        print(f'  Close Price: {self.close_price}')
        print(f'  Final Value: {self.close_value:.2f} USDT')
        print(f'  P&L: {self.profit_loss:.2f} USDT ({((self.trade_rate - 1) * 100):.2f}%)')

    def _calculate_final_values(self):
        """Calcula los valores finales de la operación"""
        open_commission = self.taker_commission
        exit_commission = self.maker_commission
        position_size = self.position_size
        entry_price = self.open_price
        exit_price = self.close_price

        units = self.position_size / entry_price

        buy_comission = position_size * open_commission
        sell_comission = units * exit_price * exit_commission
  
        total_commission = buy_comission + sell_comission
        
        if self.order_type == 'Long':
            gross_pnl = units*(exit_price-entry_price)
        else:  # Short
            gross_pnl = units*(entry_price - exit_price)        

        net_pnl = gross_pnl - total_commission

        self.close_value = self.open_value + net_pnl
        self.value_change = net_pnl
        self.profit_loss = self.value_change
        self.trade_rate = 1 + (self.profit_loss / self.open_value)

    def _calculate_profit_loss(self, current_price: float) -> float:
        """
        Calcula el P&L actual de la posición
        
        Args:
            current_price: Precio actual del mercado
            
        Returns:
            float: P&L actual en USDT
        """
        if not self.is_open:
            return self.profit_loss or 0.0
        
        if self.order_type == 'Long':
            price_change_pct = (current_price - self.open_price) / self.open_price
        else:  # Short
            price_change_pct = (self.open_price - current_price) / self.open_price
            
        gross_pnl = self.position_size * price_change_pct
        estimated_commission = self.position_size * (self.entry_commission + self.maker_commission)
        
        return gross_pnl - estimated_commission

    def _evaluate_close_conditions(self, current_price: float, high_price: float, low_price: float) -> bool:
        """
        Evalúa si la orden debe cerrarse basado en las condiciones actuales
        
        Args:
            current_price: Precio actual
            high_price: Precio más alto del período
            low_price: Precio más bajo del período
            
        Returns:
            bool: True si la orden debe cerrarse
        """
        if not self.is_open:
            return False

        # Verificar liquidación
        if self.order_type == 'Long' and low_price <= self.liquidation_price:
            self.close_price = self.liquidation_price
            return True
        elif self.order_type == 'Short' and high_price >= self.liquidation_price:
            self.close_price = self.liquidation_price
            return True

        # Verificar condiciones normales de cierre
        if self.order_type == 'Long':
            if high_price >= self.take_profit or low_price <= self.stop_loss:
                return True
        else:  # Short
            if low_price <= self.take_profit or high_price >= self.stop_loss:
                return True

        return False

    def to_dict(self) -> dict:
        """
        Convierte la orden a un diccionario, incluyendo campos específicos de futuros
        
        Returns:
            dict: Diccionario con todos los campos de la orden
        """
        base_dict = super().to_dict()
        futures_specific = {
            'taker_commission': self.taker_commission,
            'maker_commission': self.maker_commission,
            'leverage': self.leverage,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'order_type': self.order_type,
            'liquidation_price': self.liquidation_price,
            'margin': self.margin
        }
        return {**base_dict, **futures_specific}