import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .service import PolymarketClient

logger = logging.getLogger("polymarket-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    """Register all Polymarket MCP tools."""

    # ========== Gamma API Tools (Public) ==========

    @mcp.tool(
        name="polymarket_get_markets",
        description="Get list of markets from Polymarket. Returns market data including question, end date, and token information. No authentication required.",
    )
    async def polymarket_get_markets(
        limit: int = Field(
            default=100,
            description="Maximum number of markets to return",
            ge=1,
            le=1000,
        ),
        offset: int = Field(
            default=0, description="Number of markets to skip for pagination"
        ),
        active: bool = Field(default=None, description="Filter by active status"),
    ) -> str:
        """Get markets from Gamma API."""
        try:
            client = PolymarketClient()
            result = await client.get_markets(limit=limit, offset=offset, active=active)

            output = {
                "success": True,
                "count": len(result),
                "markets": [
                    {
                        "id": m.get("id"),
                        "question": m.get("question"),
                        "active": m.get("active"),
                        "closed": m.get("closed"),
                        "end_date": m.get("endDate"),
                    }
                    for m in result
                ],
            }
            logger.info(f"Retrieved {output['count']} markets")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get markets: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_get_market",
        description="Get detailed information about a specific market by ID. No authentication required.",
    )
    async def polymarket_get_market(
        market_id: str = Field(..., description="Market ID to retrieve"),
    ) -> str:
        """Get specific market details."""
        try:
            client = PolymarketClient()
            result = await client.get_market(market_id)

            output = {
                "success": True,
                "market": {
                    "id": result.get("id"),
                    "question": result.get("question"),
                    "condition_id": result.get("conditionId"),
                    "slug": result.get("slug"),
                    "end_date": result.get("endDate"),
                    "active": result.get("active"),
                    "closed": result.get("closed"),
                    "market_type": result.get("marketType"),
                    "tokens": result.get("tokens", []),
                },
            }
            logger.info(f"Retrieved market: {market_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get market {market_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_get_events",
        description="Get list of events from Polymarket. Events contain groups of related markets. No authentication required.",
    )
    async def polymarket_get_events(
        limit: int = Field(
            default=100, description="Maximum number of events to return", ge=1, le=1000
        ),
        offset: int = Field(
            default=0, description="Number of events to skip for pagination"
        ),
    ) -> str:
        """Get events from Gamma API."""
        try:
            client = PolymarketClient()
            result = await client.get_events(limit=limit, offset=offset)

            output = {
                "success": True,
                "count": len(result),
                "events": [
                    {
                        "id": e.get("id"),
                        "title": e.get("title"),
                        "slug": e.get("slug"),
                        "start_date": e.get("startDate"),
                        "end_date": e.get("endDate"),
                    }
                    for e in result
                ],
            }
            logger.info(f"Retrieved {output['count']} events")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get events: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Data API Tools (Public) ==========

    @mcp.tool(
        name="polymarket_get_user_positions",
        description="Get user positions by wallet address. Returns all positions held by the user. No authentication required.",
    )
    async def polymarket_get_user_positions(
        user_address: str = Field(..., description="Ethereum wallet address to query"),
    ) -> str:
        """Get user positions from Data API."""
        try:
            client = PolymarketClient()
            result = await client.get_user_positions(user_address)

            output = {
                "success": True,
                "user_address": user_address,
                "count": len(result),
                "positions": [
                    {
                        "position_id": p.get("positionId"),
                        "asset": p.get("asset"),
                        "quantity": p.get("quantity"),
                        "average_price": p.get("averagePrice"),
                        "current_value": p.get("currentValue"),
                    }
                    for p in result
                ],
            }
            logger.info(f"Retrieved {output['count']} positions for {user_address}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(
                f"Failed to get positions for {user_address}: {e}", exc_info=True
            )
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_get_user_trades",
        description="Get user trade history by wallet address. Returns all trades executed by the user. No authentication required.",
    )
    async def polymarket_get_user_trades(
        user_address: str = Field(..., description="Ethereum wallet address to query"),
        limit: int = Field(
            default=100, description="Maximum number of trades to return", ge=1, le=1000
        ),
        offset: int = Field(
            default=0, description="Number of trades to skip for pagination"
        ),
    ) -> str:
        """Get user trades from Data API."""
        try:
            client = PolymarketClient()
            result = await client.get_user_trades(
                user_address, limit=limit, offset=offset
            )

            output = {
                "success": True,
                "user_address": user_address,
                "count": len(result),
                "trades": [
                    {
                        "id": t.get("id"),
                        "market": t.get("market"),
                        "outcome": t.get("outcome"),
                        "side": t.get("side"),
                        "size": t.get("size"),
                        "price": t.get("price"),
                        "timestamp": t.get("timestamp"),
                    }
                    for t in result
                ],
            }
            logger.info(f"Retrieved {output['count']} trades for {user_address}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get trades for {user_address}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== CLOB API Tools (Public) ==========

    @mcp.tool(
        name="polymarket_get_orderbook",
        description="Get orderbook for a specific market. Shows bids and asks with prices and sizes. No authentication required.",
    )
    async def polymarket_get_orderbook(
        market_id: str = Field(..., description="Market ID to get orderbook for"),
    ) -> str:
        """Get orderbook from CLOB API."""
        try:
            client = PolymarketClient()
            result = await client.get_orderbook(market_id)

            output = {
                "success": True,
                "market": market_id,
                "bids": result.get("bids", []),
                "asks": result.get("asks", []),
                "timestamp": result.get("timestamp"),
            }
            logger.info(f"Retrieved orderbook for market {market_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get orderbook for {market_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_get_midpoint",
        description="Get midpoint price for a specific market. The midpoint is the average of best bid and ask. No authentication required.",
    )
    async def polymarket_get_midpoint(
        market_id: str = Field(..., description="Market ID to get midpoint for"),
    ) -> str:
        """Get midpoint price from CLOB API."""
        try:
            client = PolymarketClient()
            result = await client.get_midpoint(market_id)

            output = {
                "success": True,
                "market": market_id,
                "midpoint": result.get("midpoint"),
                "timestamp": result.get("timestamp"),
            }
            logger.info(
                f"Retrieved midpoint for market {market_id}: {output['midpoint']}"
            )
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get midpoint for {market_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== CLOB API Tools (Authenticated) ==========

    @mcp.tool(
        name="polymarket_create_order",
        description="Create a new order on Polymarket. Requires API key authentication. Order will be placed on the CLOB.",
    )
    async def polymarket_create_order(
        api_key: str = Field(..., description="Polymarket API key for authentication"),
        market_id: str = Field(..., description="Market ID to place order on"),
        side: str = Field(..., description="Order side: 'BUY' or 'SELL'"),
        price: float = Field(..., description="Order price in USD"),
        size: float = Field(..., description="Order size (number of shares)"),
        token_id: str = Field(..., description="Token ID for the market outcome"),
    ) -> str:
        """Create an order (authenticated)."""
        try:
            client = PolymarketClient(api_key=api_key)
            order_data = {
                "market": market_id,
                "side": side.upper(),
                "price": price,
                "size": size,
                "tokenId": token_id,
            }
            result = await client.create_order(order_data)

            output = {
                "success": True,
                "order_id": result.get("id"),
                "market": market_id,
                "side": side.upper(),
                "price": price,
                "size": size,
                "status": result.get("status"),
            }
            logger.info(f"Created order {output['order_id']} for market {market_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create order for {market_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_cancel_order",
        description="Cancel an existing order. Requires API key authentication.",
    )
    async def polymarket_cancel_order(
        api_key: str = Field(..., description="Polymarket API key for authentication"),
        order_id: str = Field(..., description="ID of the order to cancel"),
    ) -> str:
        """Cancel an order (authenticated)."""
        try:
            client = PolymarketClient(api_key=api_key)
            await client.cancel_order(order_id)

            output = {
                "success": True,
                "order_id": order_id,
                "message": "Order cancelled successfully",
            }
            logger.info(f"Cancelled order {order_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="polymarket_get_orders",
        description="Get user's orders. Requires API key authentication. Can filter by market.",
    )
    async def polymarket_get_orders(
        api_key: str = Field(..., description="Polymarket API key for authentication"),
        market_id: str = Field(
            default=None, description="Optional market ID to filter orders"
        ),
    ) -> str:
        """Get user's orders (authenticated)."""
        try:
            client = PolymarketClient(api_key=api_key)
            result = await client.get_orders(market_id=market_id)

            output = {
                "success": True,
                "count": len(result),
                "orders": [
                    {
                        "id": o.get("id"),
                        "market": o.get("market"),
                        "side": o.get("side"),
                        "price": o.get("price"),
                        "size": o.get("size"),
                        "status": o.get("status"),
                        "created_at": o.get("createdAt"),
                    }
                    for o in result
                ],
            }
            logger.info(f"Retrieved {output['count']} orders")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get orders: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Utility Tools ==========

    @mcp.tool(
        name="polymarket_health_check",
        description="Check server readiness and basic connectivity.",
    )
    def polymarket_health_check() -> str:
        """Health check endpoint."""
        return json.dumps(
            {
                "status": "ok",
                "server": "CL Polymarket MCP Server",
                "type": "third-party integration",
                "auth_required": "for trading operations only",
            }
        )
