from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List

class TradeType(Enum):
    LONG = auto()
    SHORT = auto()
    SPOT = auto()  # Prepared for future implementation

class TradeStatus(Enum):
    OPEN = auto()
    CLOSED = auto()

@dataclass
class TradeConfig:
    invest_size: float
    entry_price: float
    upper_close: float
    lower_close: float

class Trade(ABC):
    def __init__(self, config: TradeConfig):
        self.config = config
        self.status = TradeStatus.OPEN
        self._validate_config()

    def _validate_config(self) -> None:
        if self.config.invest_size <= 0:
            raise ValueError("Investment size must be positive")
        if self.config.entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if self.config.upper_close <= 0 or self.config.lower_close <= 0:
            raise ValueError("Close prices must be positive")

    @abstractmethod
    def calculate_return(self, close_price: float) -> float:
        pass

class ShortTrade(Trade):
    def calculate_return(self, close_price: float) -> float:
        if close_price > self.config.upper_close:
            return self.config.invest_size * (self.config.upper_close - self.config.entry_price)
        return 0.0

class LongTrade(Trade):
    def calculate_return(self, close_price: float) -> float:
        if close_price < self.config.lower_close:
            return self.config.invest_size * (self.config.entry_price - self.config.lower_close)
        return 0.0

class TransactionFactory(ABC):
    @abstractmethod
    def create_transaction(self, trade_type: TradeType, config: TradeConfig) -> Trade:
        pass

class FuturesTransactionFactory(TransactionFactory):
    def create_transaction(self, trade_type: TradeType, config: TradeConfig) -> Trade:
        trade_map = {
            TradeType.SHORT: ShortTrade,
            TradeType.LONG: LongTrade
        }
        trade_class = trade_map.get(trade_type)
        if not trade_class:
            raise ValueError(f"Unsupported trade type: {trade_type}")
        return trade_class(config)

@dataclass
class PerformanceMetrics:
    win_count: int = 0
    lose_count: int = 0
    max_winstreak: int = 0
    max_losestreak: int = 0
    max_drawdown: float = 0.0
    max_trade_rate: float = 1.0
    min_trade_rate: float = 1.0
    trade_history: List[Dict] = None

    def __post_init__(self):
        self.trade_history = []
        self._winstreak = 0
        self._losestreak = 0

class PerformanceTracker:
    def __init__(self, initial_funds: float):
        self.metrics = PerformanceMetrics(max_drawdown=initial_funds)

    def update(self, funds: float, trade_return: float, trade_info: Dict) -> None:
        self._update_winstreaks(trade_return)
        self._update_drawdown(funds)
        self._update_trade_rates(funds, trade_return)
        self._record_trade(trade_info)

    def _update_winstreaks(self, trade_return: float) -> None:
        if trade_return > 0:
            self.metrics.win_count += 1
            self.metrics._winstreak += 1
            self.metrics._losestreak = 0
            self.metrics.max_winstreak = max(
                self.metrics.max_winstreak, 
                self.metrics._winstreak
            )
        else:
            self.metrics.lose_count += 1
            self.metrics._losestreak += 1
            self.metrics._winstreak = 0
            self.metrics.max_losestreak = max(
                self.metrics.max_losestreak, 
                self.metrics._losestreak
            )

    def _update_drawdown(self, funds: float) -> None:
        self.metrics.max_drawdown = min(funds, self.metrics.max_drawdown)

    def _update_trade_rates(self, funds: float, trade_return: float) -> None:
        previous_funds = funds - trade_return
        if previous_funds != 0:
            trade_rate = funds / previous_funds
            self.metrics.max_trade_rate = max(self.metrics.max_trade_rate, trade_rate)
            self.metrics.min_trade_rate = min(self.metrics.min_trade_rate, trade_rate)

    def _record_trade(self, trade_info: Dict) -> None:
        self.metrics.trade_history.append(trade_info)

class Trader(ABC):
    @property
    @abstractmethod
    def current_trade(self) -> Optional[Trade]:
        pass

    @property
    @abstractmethod
    def funds(self) -> float:
        pass

    @property
    @abstractmethod
    def performance_tracker(self) -> PerformanceTracker:
        pass

    @abstractmethod
    def open_position(self, trade_type: TradeType, config: TradeConfig) -> None:
        pass

    @abstractmethod
    def close_position(self, close_price: float) -> None:
        pass

class FuturesTrader(Trader):
    def __init__(
        self, 
        initial_funds: float,
        transaction_factory: TransactionFactory,
        performance_tracker: Optional[PerformanceTracker] = None
    ):
        self._funds = initial_funds
        self._transaction_factory = transaction_factory
        self._performance_tracker = performance_tracker or PerformanceTracker(initial_funds)
        self._current_trade: Optional[Trade] = None

    @property
    def current_trade(self) -> Optional[Trade]:
        return self._current_trade

    @property
    def funds(self) -> float:
        return self._funds

    @property
    def performance_tracker(self) -> PerformanceTracker:
        return self._performance_tracker

    def open_position(self, trade_type: TradeType, config: TradeConfig) -> None:
        if not self._current_trade and self._transaction_factory:
            self._current_trade = self._transaction_factory.create_transaction(
                trade_type, config
            )

    def close_position(self, close_price: float) -> None:
        if self._current_trade:
            trade_return = self._current_trade.calculate_return(close_price)
            self._update_funds(trade_return)

            trade_info = {
                'close_price': close_price,
                'return': trade_return,
                'final_funds': self._funds
            }

            self._performance_tracker.update(self._funds, trade_return, trade_info)
            self._reset_position()

    def _update_funds(self, trade_return: float) -> None:
        self._funds += trade_return

    def _reset_position(self) -> None:
        self._current_trade = None

class Signal(Enum):
    BUY = auto()
    SELL = auto()
    NONE = auto()

@dataclass
class SignalData:
    signal: Signal
    take_profit: float
    stop_loss: float

class SignalProcessor:
    def __init__(self):
        self._current_signal = SignalData(Signal.NONE, 0.0, 0.0)

    @property
    def current_signal(self) -> SignalData:
        return self._current_signal

    def update_signal(self, signal: Signal, take_profit: float, stop_loss: float) -> None:
        self._current_signal = SignalData(signal, take_profit, stop_loss)

class TradeExecutor:
    def __init__(self, trader: Trader, risk_percentage: float = 1):
        self._trader = trader
        self._risk_percentage = risk_percentage
        self._total_trades = 0

    @property
    def total_trades(self) -> int:
        return self._total_trades

    def execute_trade(self, signal: Signal, price: float, tp: float, sl: float) -> None:
        if self._trader.current_trade is None:
            self._open_new_position(signal, price, tp, sl)
        else:
            self._trader.close_position(price)

    def _open_new_position(self, signal: Signal, price: float, tp: float, sl: float) -> None:
        self._total_trades += 1
        invest_size = self._trader.funds * self._risk_percentage

        config = TradeConfig(
            invest_size=invest_size,
            entry_price=price,
            upper_close=tp if signal == Signal.BUY else sl,
            lower_close=sl if signal == Signal.BUY else tp
        )

        trade_type = TradeType.LONG if signal == Signal.BUY else TradeType.SHORT
        self._trader.open_position(trade_type, config)

class StrategyManager:
    def __init__(
        self,
        initial_signal: Signal,
        take_profit: float,
        stop_loss: float,
        trader: Optional[Trader] = None
    ):
        self._signal_processor = SignalProcessor()
        self._trader = trader or FuturesTrader(
            100.0,
            FuturesTransactionFactory()
        )
        self._trade_executor = TradeExecutor(self._trader)
        self._signal_processor.update_signal(initial_signal, take_profit, stop_loss)

    def update_strategy(self, signal: Signal, price: float, take_profit: float, stop_loss: float) -> None:
        self._signal_processor.update_signal(signal, take_profit, stop_loss)
        self._trade_executor.execute_trade(signal, price, take_profit, stop_loss)

    @property
    def current_funds(self) -> float:
        return self._trader.funds

    def get_performance_report(self) -> str:
        pt = self._trader.performance_tracker.metrics
        win_rate = (pt.win_count / self._trade_executor.total_trades * 100) if self._trade_executor.total_trades > 0 else 0
        return (
            f"Performance Report\n"
            f"================\n"
            f"Final funds: {self._trader.funds:.2f}\n"
            f"Total trades: {self._trade_executor.total_trades}\n"
            f"Win trades: {pt.win_count}\n"
            f"Lose trades: {pt.lose_count}\n"
            f"Win rate: {win_rate:.2f}%\n"
            f"Max trade rate: {pt.max_trade_rate:.2f}\n"
            f"Min trade rate: {pt.min_trade_rate:.2f}\n"
            f"Max win streak: {pt.max_winstreak}\n"
            f"Max lose streak: {pt.max_losestreak}\n"
            f"Max drawdown: {pt.max_drawdown:.2f}"
        )