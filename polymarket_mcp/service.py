import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastmcp_credentials import get_credentials

from .config import CLOB_API_BASE, DATA_API_BASE, DEFAULT_HEADERS, GAMMA_API_BASE

logger = logging.getLogger("polymarket-mcp-server")


class PolymarketClient:
    """Client for Polymarket APIs (Gamma, Data, CLOB)."""

    def __init__(self):
        cred = get_credentials()
        self.api_key = cred.fields.get("api_key")
        self.headers = DEFAULT_HEADERS.copy()
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    async def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request to API."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers or self.headers,
                params=params,
                json=json_data,
                timeout=30.0,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()

    # Gamma API (Public)

    async def get_markets(
        self, limit: int = 100, offset: int = 0, active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get markets from Gamma API."""
        params = {"limit": limit, "offset": offset}
        if active is not None:
            params["active"] = active
        return await self._request("GET", f"{GAMMA_API_BASE}/markets", params=params)

    async def get_market(self, market_id: str) -> Dict[str, Any]:
        """Get specific market by ID."""
        return await self._request("GET", f"{GAMMA_API_BASE}/markets/{market_id}")

    async def get_events(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get events from Gamma API."""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", f"{GAMMA_API_BASE}/events", params=params)

    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get specific event by ID."""
        return await self._request("GET", f"{GAMMA_API_BASE}/events/{event_id}")

    # Data API (Public)

    async def get_user_positions(self, user_address: str) -> List[Dict[str, Any]]:
        """Get user positions from Data API."""
        return await self._request("GET", f"{DATA_API_BASE}/positions/{user_address}")

    async def get_user_trades(
        self, user_address: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user trades from Data API."""
        params = {"limit": limit, "offset": offset}
        return await self._request(
            "GET", f"{DATA_API_BASE}/trades/{user_address}", params=params
        )

    async def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard from Data API."""
        params = {"limit": limit}
        return await self._request("GET", f"{DATA_API_BASE}/leaderboard", params=params)

    # CLOB API (Public)

    async def get_orderbook(self, market_id: str) -> Dict[str, Any]:
        """Get orderbook for a market."""
        return await self._request("GET", f"{CLOB_API_BASE}/book/{market_id}")

    async def get_midpoint(self, market_id: str) -> Dict[str, Any]:
        """Get midpoint price for a market."""
        return await self._request("GET", f"{CLOB_API_BASE}/midpoint/{market_id}")

    async def get_price_history(
        self, market_id: str, interval: str = "1h", limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get price history for a market."""
        params = {"interval": interval, "limit": limit}
        return await self._request(
            "GET", f"{CLOB_API_BASE}/prices/{market_id}", params=params
        )

    # CLOB API (Authenticated)

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order (requires API key)."""
        if not self.api_key:
            raise ValueError("API key required for order creation")
        return await self._request(
            "POST", f"{CLOB_API_BASE}/order", json_data=order_data
        )

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order (requires API key)."""
        if not self.api_key:
            raise ValueError("API key required for order cancellation")
        await self._request("DELETE", f"{CLOB_API_BASE}/order/{order_id}")
        return True

    async def get_orders(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's orders (requires API key)."""
        if not self.api_key:
            raise ValueError("API key required for fetching orders")
        params = {}
        if market_id:
            params["market"] = market_id
        return await self._request("GET", f"{CLOB_API_BASE}/orders", params=params)
