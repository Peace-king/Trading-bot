"""
Order placement logic.
Sits between the CLI layer and the raw BinanceClient.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import BinanceClient

from .logging_config import get_logger
from .validators import validate_order_params

logger = get_logger(__name__)


class OrderManager:
    """High-level order operations on top of BinanceClient."""

    def __init__(self, client: BinanceClient):
        self.client = client

    # ------------------------------------------------------------------
    # Core order methods
    # ------------------------------------------------------------------

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Place a MARKET order."""
        params = validate_order_params(symbol, side, "MARKET", quantity)
        logger.info(
            "Placing MARKET %s order | symbol=%s qty=%s",
            params["side"], params["symbol"], params["quantity"],
        )
        result = self.client.place_order(**params)
        logger.info("MARKET order placed | orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        """Place a LIMIT order."""
        params = validate_order_params(symbol, side, "LIMIT", quantity, price=price)
        logger.info(
            "Placing LIMIT %s order | symbol=%s qty=%s price=%s",
            params["side"], params["symbol"], params["quantity"], params["price"],
        )
        result = self.client.place_order(**params)
        logger.info("LIMIT order placed | orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result

    def place_stop_market_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Place a STOP_MARKET order (bonus order type)."""
        params = validate_order_params(symbol, side, "STOP_MARKET", quantity, stop_price=stop_price)
        logger.info(
            "Placing STOP_MARKET %s order | symbol=%s qty=%s stopPrice=%s",
            params["side"], params["symbol"], params["quantity"], params["stopPrice"],
        )
        result = self.client.place_order(**params)
        logger.info("STOP_MARKET order placed | orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result


# ------------------------------------------------------------------
# Output formatting
# ------------------------------------------------------------------

def format_order_summary(params: dict) -> str:
    lines = [
        "─" * 46,
        "  ORDER REQUEST SUMMARY",
        "─" * 46,
        f"  Symbol     : {params.get('symbol')}",
        f"  Side       : {params.get('side')}",
        f"  Type       : {params.get('type')}",
        f"  Quantity   : {params.get('quantity')}",
    ]
    if "price" in params:
        lines.append(f"  Price      : {params['price']}")
    if "stopPrice" in params:
        lines.append(f"  Stop Price : {params['stopPrice']}")
    lines.append("─" * 46)
    return "\n".join(lines)


def format_order_response(result: dict) -> str:
    lines = [
        "─" * 46,
        "  ORDER RESPONSE",
        "─" * 46,
        f"  Order ID   : {result.get('orderId', 'N/A')}",
        f"  Status     : {result.get('status', 'N/A')}",
        f"  Exec Qty   : {result.get('executedQty', 'N/A')}",
        f"  Avg Price  : {result.get('avgPrice', 'N/A')}",
        f"  Client OID : {result.get('clientOrderId', 'N/A')}",
        "─" * 46,
    ]
    return "\n".join(lines)
