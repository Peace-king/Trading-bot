"""Binance Futures Testnet trading bot package."""
from .logging_config import configure_logging

__all__ = ["configure_logging"]


def __getattr__(name):
    if name == "BinanceClient":
        from .client import BinanceClient
        return BinanceClient
    if name == "OrderManager":
        from .orders import OrderManager
        return OrderManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
