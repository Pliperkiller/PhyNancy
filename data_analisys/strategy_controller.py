from abc import ABC, abstractmethod

# MANAGE LONG AND SHORT TRADES 
# TO DO// SPOT TRADES

class Trade(ABC):
    def __init__(self, invest_size, entry_price, upper_close, lower_close):
        self.invest_size = invest_size
        self.entry_price = entry_price
        self.upper_close = upper_close
        self.lower_close = lower_close
        self.status = 'open'

    @abstractmethod
    def calculate_return(self, close_price):
        pass

class ShortTrade(Trade):
    def calculate_return(self, close_price):
        if close_price > self.upper_close:
            return self.invest_size * (self.upper_close - self.entry_price)
        return 0

class LongTrade(Trade):
    def calculate_return(self, close_price):
        if close_price < self.lower_close:
            return self.invest_size * (self.entry_price - self.lower_close)
        return 0


# BUILD TRANSACTIONS
# TO DO// SPOT TransactionFactory

class ITransactionFactory(ABC):
    @abstractmethod
    def create_transaction(self, trade_type, invest_size, entry_price, upper_close, lower_close):
        pass

class FuturesTransactionFactory(ITransactionFactory):
    @staticmethod
    def create_transaction(trade_type, invest_size, entry_price, upper_close, lower_close):
        if trade_type == 'short':
            return ShortTrade(invest_size, entry_price, upper_close, lower_close)
        elif trade_type == 'long':
            return LongTrade(invest_size, entry_price, upper_close, lower_close)
        else:
            raise ValueError("Invalid trade type")


# Holds buyer statistic info for all trades made by the strategy

class PerformanceTracker:
    def __init__(self, initial_funds):
        self.win_count = 0
        self.lose_count = 0
        self.max_winstreak = 0
        self.max_losestreak = 0
        self._winstreak = 0
        self._losestreak = 0
        self.max_drawdown = initial_funds
        self.max_trade_rate = 1
        self.min_trade_rate = 1

    def update(self, funds, trade_return):
        self._update_winstreaks(trade_return)
        self._update_drawdown(funds)
        self._update_trade_rates(funds, trade_return)

    def _update_winstreaks(self, trade_return):
        if trade_return > 0:
            self.win_count += 1
            self._winstreak += 1
            self._losestreak = 0
            self.max_winstreak = max(self.max_winstreak, self._winstreak)
        else:
            self.lose_count += 1
            self._losestreak += 1
            self._winstreak = 0
            self.max_losestreak = max(self.max_losestreak, self._losestreak)

    def _update_drawdown(self, funds):
        self.max_drawdown = min(funds, self.max_drawdown)

    def _update_trade_rates(self, funds, trade_return):
        previous_funds = funds - trade_return
        trade_rate = (funds / previous_funds) if previous_funds != 0 else 1
        self.max_trade_rate = max(self.max_trade_rate, trade_rate)
        self.min_trade_rate = min(self.min_trade_rate, trade_rate)

# Generate orders to TransactionFactory and sends stats to the performance tracker
# TO DO// SPOT Buyer

class ITrader(ABC):
    @property
    @abstractmethod
    def current_trade(self):
        pass

    @property
    @abstractmethod
    def funds(self):
        pass

    @property
    @abstractmethod
    def performance_tracker(self) -> PerformanceTracker:
        pass

    @abstractmethod
    def buy(self, trade_type, invest_size, entry_price, upper_close, lower_close):
        pass

    @abstractmethod
    def sell(self, close_price):
        pass

class FuturesBuyer(ITrader):
    def __init__(self, funds=100, transaction_factory=None, performance_tracker=None):
        self.funds = funds
        self.transaction_factory: ITransactionFactory = transaction_factory
        self.performance_tracker: PerformanceTracker = performance_tracker or PerformanceTracker(funds)
        self.current_trade: Trade = None

    def buy(self, trade_type, invest_size, entry_price, upper_close, lower_close):
        if not self.current_trade and self.transaction_factory:
            self.current_trade = self.transaction_factory.create_transaction(
                trade_type, invest_size, entry_price, upper_close, lower_close
            )

    def sell(self, close_price):
        if self.current_trade:
            trade_return = self.current_trade.calculate_return(close_price)
            self._update_funds(trade_return)
            self.performance_tracker.update(self.funds, trade_return)
            self._reset_trade()

    def _update_funds(self, trade_return):
        self.funds += trade_return

    def _reset_trade(self):
        self.current_trade = None





# Read and stores signal information
# TO DO// SPOT
class SignalProcessor:
    def __init__(self):
        self.signal = None
        self.tp = 0
        self.sl = 0

    def update_signal(self, signal, tp, sl):
        self.signal = signal
        self.tp = tp
        self.sl = sl


# Reads signal, tp, sl an sends transaction order to the buyer
class TradeExecutor:
    def __init__(self, buyer):
        self.buyer: ITrader = buyer
        self.total_trades = 0

    def execute_trade(self, signal, price, tp, sl):
        if self.buyer.current_trade is None:
            self.total_trades += 1
            invest_size = self.buyer.funds * 0.1
            entry_price = price

            if signal == 'buy':
                trade_type = 'long'
                upper_close = tp
                lower_close = sl
            elif signal == 'sell':
                trade_type = 'short'
                upper_close = sl
                lower_close = tp
            else:
                return

            self.buyer.buy(trade_type, invest_size, entry_price, upper_close, lower_close)

        elif self.buyer.current_trade:
            self.buyer.sell(price)



class StrategyManager:
    def __init__(self, initial_signal, tp, sl,buyer: ITrader=FuturesBuyer()):
        self.signal_processor = SignalProcessor()
        self.buyer = buyer
        self.trade_executor = TradeExecutor(self.buyer)
        self.signal_processor.update_signal(initial_signal, tp, sl)

    def check_strategy(self, signal, price, tp, sl):
        self.signal_processor.update_signal(signal, tp, sl)
        self.trade_executor.execute_trade(signal, price, tp, sl)

    def report_funds(self):
        return self.buyer.funds

    def print_stats(self):
        pt = self.buyer.performance_tracker
        print(
            f'Final funds: {self.buyer.funds}',
            f'Total trades: {self.trade_executor.total_trades}',
            f'Win trades: {pt.win_count}',
            f'Lose trades: {pt.lose_count}',
            f'Max trade rate: {pt.max_trade_rate}',
            f'Min trade rate: {pt.min_trade_rate}',
            f'Max win streak: {pt.max_winstreak}',
            f'Max lose streak: {pt.max_losestreak}',
            f'Max drawdown: {pt.max_drawdown}',
            sep='\n'
        )
