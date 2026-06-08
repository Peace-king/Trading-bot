"""
Binance Futures Testnet Client Wrapper
Handles authentication and raw API communication.
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx

from .logging_config import get_logger

logger = get_logger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """Low-level REST client for Binance Futures Testnet."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=10.0,
        )

    # ------------------------------------------------------------------
    # Signature helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None, signed: bool = False) -> dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        logger.debug("GET %s params=%s", path, params)
        response = self._client.get(path, params=params)
        return self._handle_response(response)

    def _post(self, path: str, params: dict | None = None, signed: bool = True) -> dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        logger.debug("POST %s params=%s", path, {k: v for k, v in params.items() if k != "signature"})
        response = self._client.post(path, data=params)
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: httpx.Response) -> dict:
        try:
            data = response.json()
        except Exception as exc:
            logger.error("Failed to parse response: %s", response.text)
            raise ValueError(f"Non-JSON response: {response.text}") from exc

        if response.is_error:
            code = data.get("code", response.status_code)
            msg = data.get("msg", "Unknown error")
            logger.error("API error %s: %s", code, msg)
            raise RuntimeError(f"Binance API error {code}: {msg}")

        logger.debug("Response: %s", data)
        return data

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    def ping(self) -> dict:
        """Check server connectivity."""
        return self._get("/fapi/v1/ping")

    def get_exchange_info(self) -> dict:
        """Fetch exchange metadata (symbols, filters, etc.)."""
        return self._get("/fapi/v1/exchangeInfo")

    # ------------------------------------------------------------------
    # Order endpoints
    # ------------------------------------------------------------------

    def place_order(self, **kwargs) -> dict:
        """Place a new order. kwargs become POST parameters."""
        return self._post("/fapi/v1/order", params=kwargs)

    def get_order(self, symbol: str, order_id: int) -> dict:
        return self._get("/fapi/v1/order", params={"symbol": symbol, "orderId": order_id}, signed=True)

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        params = self._sign(params)
        response = self._client.delete("/fapi/v1/order", params=params)
        return self._handle_response(response)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
