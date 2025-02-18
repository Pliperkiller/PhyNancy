from typing import Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Candle:
    """Class to store candle information"""
    open: float
    high: float
    low: float
    close: float
    timestamp: datetime
    signal: Optional[int] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None