"""MewCP Polymarket tool registration."""

from fastmcp import FastMCP

from .events_tools import register_events_tools
from .markets_tools import register_markets_tools
from .asset_prices_tools import register_asset_prices_tools
from .series_tools import register_series_tools
from .sports_tools import register_sports_tools
from .tags_tools import register_tags_tools
from .search_tools import register_search_tools
from .orders_tools import register_orders_tools
from .portfolio_tools import register_portfolio_tools
from .account_tools import register_account_tools
from .incentives_tools import register_incentives_tools


def register_tools(mcp: FastMCP) -> None:
    register_events_tools(mcp)
    register_markets_tools(mcp)
    register_asset_prices_tools(mcp)
    register_series_tools(mcp)
    register_sports_tools(mcp)
    register_tags_tools(mcp)
    register_search_tools(mcp)
    register_orders_tools(mcp)
    register_portfolio_tools(mcp)
    register_account_tools(mcp)
    register_incentives_tools(mcp)
