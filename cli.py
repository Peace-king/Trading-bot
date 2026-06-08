#!/usr/bin/env python3
"""
cli.py — Command-line interface for the Binance Futures Testnet trading bot.

Usage examples:
  python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000
  python cli.py place-order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000
  python cli.py ping
"""

import os
import sys
import argparse

from dotenv import load_dotenv

from bot import BinanceClient, OrderManager, configure_logging
from bot.orders import format_order_summary, format_order_response
from bot.validators import validate_order_params
from bot.logging_config import get_logger

load_dotenv()
configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print(
            "\n[ERROR] Missing API credentials.\n"
            "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file or environment.\n"
        )
        sys.exit(1)
    return api_key, api_secret


def success(msg: str) -> None:
    print(f"\n✅  {msg}\n")


def failure(msg: str) -> None:
    print(f"\n❌  {msg}\n")


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_ping(args) -> None:  # noqa: ARG001
    api_key, api_secret = get_credentials()
    with BinanceClient(api_key, api_secret) as client:
        try:
            client.ping()
            success("Testnet is reachable.")
        except Exception as exc:
            failure(f"Ping failed: {exc}")
            sys.exit(1)


def cmd_place_order(args) -> None:
    api_key, api_secret = get_credentials()

    # Validate inputs up-front (before touching the network)
    try:
        params = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        failure(f"Validation error: {exc}")
        logger.error("Validation error: %s", exc)
        sys.exit(1)

    print(format_order_summary(params))

    with BinanceClient(api_key, api_secret) as client:
        manager = OrderManager(client)
        try:
            order_type = params["type"]
            if order_type == "MARKET":
                result = manager.place_market_order(params["symbol"], params["side"], params["quantity"])
            elif order_type == "LIMIT":
                result = manager.place_limit_order(
                    params["symbol"], params["side"], params["quantity"], params["price"]
                )
            elif order_type == "STOP_MARKET":
                result = manager.place_stop_market_order(
                    params["symbol"], params["side"], params["quantity"], params["stopPrice"]
                )
            else:
                failure(f"Unhandled order type: {order_type}")
                sys.exit(1)

            print(format_order_response(result))
            success("Order placed successfully.")
            logger.info("Order complete: %s", result)

        except RuntimeError as exc:
            failure(f"API error: {exc}")
            logger.error("Order failed: %s", exc)
            sys.exit(1)
        except Exception as exc:
            failure(f"Unexpected error: {exc}")
            logger.exception("Unexpected error during order placement")
            sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet trading bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ping
    subparsers.add_parser("ping", help="Check testnet connectivity")

    # place-order
    po = subparsers.add_parser("place-order", help="Place a futures order")
    po.add_argument("--symbol", required=True, help="Trading pair (e.g. BTCUSDT)")
    po.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    po.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type",
    )
    po.add_argument("--quantity", required=True, type=float, help="Order quantity")
    po.add_argument("--price", type=float, default=None, help="Limit price (required for LIMIT)")
    po.add_argument("--stop-price", dest="stop_price", type=float, default=None,
                    help="Stop price (required for STOP_MARKET)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ping":
        cmd_ping(args)
    elif args.command == "place-order":
        cmd_place_order(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
