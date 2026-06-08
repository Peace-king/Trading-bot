"""
Input validation for order parameters.
Raises ValueError with a human-readable message on invalid input.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}
VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK", "GTX"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}': must be alphanumeric (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}': must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Invalid order type '{order_type}': must be one of {VALID_ORDER_TYPES}.")
    return order_type


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}': must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price: str | float) -> float:
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}': must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be positive, got {p}.")
    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> dict:
    """Validate all order parameters and return a clean dict ready for the API."""
    params: dict = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    order_type_clean = params["type"]

    if order_type_clean == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        params["price"] = validate_price(price)
        params["timeInForce"] = "GTC"

    elif order_type_clean == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("stopPrice is required for STOP_MARKET orders.")
        params["stopPrice"] = validate_price(stop_price)

    return params
