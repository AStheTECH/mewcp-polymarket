"""Markets group: list_markets, get_market_by_id, get_market_by_slug, get_market_bbo,
get_market_book, get_market_settlement, get_price_history."""

import logging
from typing import Literal
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.markets import (
    GetMarketBboData,
    GetMarketBboResult,
    GetMarketBookData,
    GetMarketBookResult,
    GetMarketByIdData,
    GetMarketByIdResult,
    GetMarketBySlugData,
    GetMarketBySlugResult,
    GetMarketSettlementData,
    GetMarketSettlementResult,
    GetPriceHistoryData,
    GetPriceHistoryResult,
    ListMarketsData,
    ListMarketsResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.markets")

_READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)
_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

SportsMarketType = Literal[
    "SPORTS_MARKET_TYPE_MONEYLINE",
    "SPORTS_MARKET_TYPE_SPREAD",
    "SPORTS_MARKET_TYPE_TOTAL",
    "SPORTS_MARKET_TYPE_PROP",
    "SPORTS_MARKET_TYPE_FUTURE",
    "SPORTS_MARKET_TYPE_DRAWABLE_OUTCOME",
]

FixedInterval = Literal[
    "INTERVAL_ALL",
    "INTERVAL_1M",
    "INTERVAL_1W",
    "INTERVAL_1D",
    "INTERVAL_6H",
    "INTERVAL_1H",
    "INTERVAL_LIVE",
]


def register_markets_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_markets",
        description=(
            "Lists markets, optionally filtered by IDs, slugs, status flags, volume range, start/end dates, "
            "categories, market types, tag IDs, game ID or sports market types, with limit/offset paging. "
            "Returns market records including slug, question, status, sides, best bid/ask quotes, tags and volume. "
            "Hidden markets are excluded unless includeHidden is true. The returned `slug` is the identifier "
            "used by get_market_by_slug, get_market_book, get_market_bbo, get_market_settlement, "
            "get_price_history (as `symbol`) and order creation (as `marketSlug`)."
        ),
        annotations=_READ_ONLY,
    )
    def list_markets(
        limit: int | None = Field(default=None, description="Page size. Omit for the API default."),
        offset: int | None = Field(default=None, description="Number of markets to skip for paging. Omit to start at the first market."),
        orderBy: list[str] | None = Field(default=None, description="Fields to order results by. Omit for the API default ordering."),
        orderDirection: str | None = Field(default=None, description="Order direction applied to orderBy. Omit for the API default."),
        market_ids: list[int] | None = Field(default=None, description="Return only markets with these numeric IDs. Omit to not filter by ID."),
        slug: list[str] | None = Field(default=None, description="Return only markets with these slugs. Omit to not filter by slug."),
        archived: bool | None = Field(default=None, description="Filter by whether the market is archived. Omit to not filter."),
        active: bool | None = Field(default=None, description="Filter by whether the market is active. Omit to not filter."),
        closed: bool | None = Field(default=None, description="Filter by whether the market is closed. Omit to not filter."),
        volumeNumMin: float | None = Field(default=None, description="Minimum market volume. Omit for no lower bound."),
        volumeNumMax: float | None = Field(default=None, description="Maximum market volume. Omit for no upper bound."),
        startDateMin: str | None = Field(default=None, description="Earliest market start date (date string). Omit for no lower bound."),
        startDateMax: str | None = Field(default=None, description="Latest market start date (date string). Omit for no upper bound."),
        endDateMin: str | None = Field(default=None, description="Earliest market end date (date string). Omit for no lower bound."),
        endDateMax: str | None = Field(default=None, description="Latest market end date (date string). Omit for no upper bound."),
        relatedTags: bool | None = Field(default=None, description="Whether related tags are enabled for the tag filter. Omit for the API default."),
        gameId: str | None = Field(default=None, description="Return only markets for this game ID. Omit to not filter by game."),
        sportsMarketTypes: list[SportsMarketType] | None = Field(default=None, description="Return only markets of these sports market types. Omit to not filter."),
        includeTag: bool | None = Field(default=None, description="Whether to include tag data on each market. Omit for the API default."),
        categories: list[str] | None = Field(default=None, description="Return only markets in these categories (e.g. sports, crypto). Omit to not filter."),
        marketTypes: list[str] | None = Field(default=None, description="Return only markets of these market types. Omit to not filter."),
        includeHidden: bool = Field(default=False, description="Include hidden markets. Defaults to false."),
        tagIds: list[int] | None = Field(default=None, description="Return only markets with these tag IDs. Omit to not filter by tag."),
    ) -> ListMarketsResult:
        tlog = ToolLogger(logger, "list_markets")
        params = {
            "limit": limit,
            "offset": offset,
            "orderBy": orderBy,
            "orderDirection": orderDirection,
            "id": market_ids,
            "slug": slug,
            "archived": archived,
            "active": active,
            "closed": closed,
            "volumeNumMin": volumeNumMin,
            "volumeNumMax": volumeNumMax,
            "startDateMin": startDateMin,
            "startDateMax": startDateMax,
            "endDateMin": endDateMin,
            "endDateMax": endDateMax,
            "relatedTags": relatedTags,
            "gameId": gameId,
            "sportsMarketTypes": sportsMarketTypes,
            "includeTag": includeTag,
            "categories": categories,
            "marketTypes": marketTypes,
            "includeHidden": includeHidden,
            "tagIds": tagIds,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/markets", params=params, timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = ListMarketsResult(success=True, statusCode=status, data=ListMarketsData(**data))
                tlog.success()
                return result
            return _upstream_err(ListMarketsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListMarketsResult, tlog, exc)

    @mcp.tool(
        name="get_market_by_id",
        description=(
            "Retrieves one market by its numeric ID. Returns the market's full details: question, slug, "
            "status, dates, sides, best bid/ask quotes, tags, subject, price terms and volume."
        ),
        annotations=_READ_ONLY,
    )
    def get_market_by_id(
        market_id: int = Field(description="Numeric market ID (from list_markets)."),
    ) -> GetMarketByIdResult:
        tlog = ToolLogger(logger, "get_market_by_id")
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/market/id/{market_id}", timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetMarketByIdResult(success=True, statusCode=status, data=GetMarketByIdData(**data))
                tlog.success()
                return result
            return _upstream_err(GetMarketByIdResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetMarketByIdResult, tlog, exc)

    @mcp.tool(
        name="get_market_by_slug",
        description=(
            "Retrieves one market by its slug. Returns the market's full details: question, ID, "
            "status, dates, sides, best bid/ask quotes, tags, subject, price terms and volume."
        ),
        annotations=_READ_ONLY,
    )
    def get_market_by_slug(
        slug: str = Field(description="Market slug (from list_markets), e.g. 'btc-100k-2025'."),
    ) -> GetMarketBySlugResult:
        tlog = ToolLogger(logger, "get_market_by_slug")
        if not slug.strip():
            return _err(GetMarketBySlugResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/market/slug/{quote(slug, safe='')}", timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetMarketBySlugResult(success=True, statusCode=status, data=GetMarketBySlugData(**data))
                tlog.success()
                return result
            return _upstream_err(GetMarketBySlugResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetMarketBySlugResult, tlog, exc)

    @mcp.tool(
        name="get_market_bbo",
        description=(
            "Retrieves lightweight live market data for one market by slug. Returns best bid and best ask, "
            "current and last-trade prices, settlement price, long/short quotes, shares traded, open interest, "
            "book depth (price-level counts and resting shares per side) and the book state. "
            "Use get_market_book for the full order book."
        ),
        annotations=_READ_ONLY,
    )
    def get_market_bbo(
        slug: str = Field(description="Market slug (from list_markets), e.g. 'btc-100k-2025'."),
    ) -> GetMarketBboResult:
        tlog = ToolLogger(logger, "get_market_bbo")
        if not slug.strip():
            return _err(GetMarketBboResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/markets/{quote(slug, safe='')}/bbo", timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetMarketBboResult(success=True, statusCode=status, data=GetMarketBboData(**data))
                tlog.success()
                return result
            return _upstream_err(GetMarketBboResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetMarketBboResult, tlog, exc)

    @mcp.tool(
        name="get_market_book",
        description=(
            "Retrieves the order book for one market by slug. Returns bid and offer price levels "
            "(price and quantity), the book state, the transaction time and market stats "
            "(open/close/high/low/last-trade prices, settlement price and method, shares and notional traded, "
            "open interest). Use get_market_bbo when only the best bid/offer is needed."
        ),
        annotations=_READ_ONLY,
    )
    def get_market_book(
        slug: str = Field(description="Market slug (from list_markets), e.g. 'btc-100k-2025'."),
    ) -> GetMarketBookResult:
        tlog = ToolLogger(logger, "get_market_book")
        if not slug.strip():
            return _err(GetMarketBookResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/markets/{quote(slug, safe='')}/book", timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetMarketBookResult(success=True, statusCode=status, data=GetMarketBookData(**data))
                tlog.success()
                return result
            return _upstream_err(GetMarketBookResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetMarketBookResult, tlog, exc)

    @mcp.tool(
        name="get_market_settlement",
        description=(
            "Retrieves the settlement price of one market by slug. Returns the market slug and its "
            "settlement price as a number."
        ),
        annotations=_READ_ONLY,
    )
    def get_market_settlement(
        slug: str = Field(description="Market slug (from list_markets), e.g. 'btc-100k-2025'."),
    ) -> GetMarketSettlementResult:
        tlog = ToolLogger(logger, "get_market_settlement")
        if not slug.strip():
            return _err(GetMarketSettlementResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/markets/{quote(slug, safe='')}/settlement", timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetMarketSettlementResult(
                    success=True, statusCode=status, data=GetMarketSettlementData(**data))
                tlog.success()
                return result
            return _upstream_err(GetMarketSettlementResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetMarketSettlementResult, tlog, exc)

    @mcp.tool(
        name="get_price_history",
        description=(
            "Retrieves book-derived Yes (longPrice, normally from the best ask) and No (shortPrice, normally "
            "one minus the best bid) display prices over time for one market, as Unix-second timestamped points. "
            "These are not trades, and the two prices can sum to more than 1 because they keep the bid-ask spread. "
            "Pass either fixedInterval with its matching fidelity (1H/6H/LIVE: 1, 1D: 5, 1W/1M/ALL: 180) or both "
            "start_timestamp and end_timestamp with fidelity 1; custom ranges are meant for windows up to 24 hours "
            "and may return irregular points. One market per call; an unknown slug or a market without stored "
            "observations returns an empty history. Responses are cached for 30 seconds."
        ),
        annotations=_READ_ONLY,
    )
    def get_price_history(
        symbol: str = Field(description="Market slug (from list_markets), e.g. 'btc-100k-2025'."),
        fidelity: int = Field(
            description="Point spacing in minutes (minimum 1). Use 1 for INTERVAL_1H, INTERVAL_6H, INTERVAL_LIVE "
                        "and timestamp ranges; 5 for INTERVAL_1D; 180 for INTERVAL_1W, INTERVAL_1M, INTERVAL_ALL."),
        fixedInterval: FixedInterval | None = Field(
            default=None,
            description="Fixed history window: INTERVAL_1H (last hour), INTERVAL_6H, INTERVAL_1D, INTERVAL_1W, "
                        "INTERVAL_1M (last 30 days), INTERVAL_ALL, or INTERVAL_LIVE (from 15 minutes before the event "
                        "starts through now). Cannot be combined with start_timestamp/end_timestamp."),
        start_timestamp: int | None = Field(
            default=None,
            description="Custom range start in Unix seconds. Requires end_timestamp; cannot be combined with fixedInterval."),
        end_timestamp: int | None = Field(
            default=None,
            description="Custom range end in Unix seconds. Requires start_timestamp; cannot be combined with fixedInterval."),
    ) -> GetPriceHistoryResult:
        tlog = ToolLogger(logger, "get_price_history")
        if not symbol.strip():
            return _err(GetPriceHistoryResult, tlog, "VALIDATION_ERROR", "symbol must not be empty", 400)
        if fidelity < 1:
            return _err(GetPriceHistoryResult, tlog, "VALIDATION_ERROR", "fidelity must be at least 1", 400)
        if (start_timestamp is None) != (end_timestamp is None):
            return _err(GetPriceHistoryResult, tlog, "VALIDATION_ERROR",
                        "start_timestamp and end_timestamp must be provided together", 400)
        if fixedInterval is not None and start_timestamp is not None:
            return _err(GetPriceHistoryResult, tlog, "VALIDATION_ERROR",
                        "fixedInterval cannot be combined with start_timestamp/end_timestamp", 400)
        params = {
            "symbol": symbol,
            "fixedInterval": fixedInterval,
            "timestamp.startTimestamp": start_timestamp,
            "timestamp.endTimestamp": end_timestamp,
            "fidelity": fidelity,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/price-history", params=params, timeout=_TIMEOUT)
            if 200 <= status < 300:
                result = GetPriceHistoryResult(success=True, statusCode=status, data=GetPriceHistoryData(**data))
                tlog.success()
                return result
            return _upstream_err(GetPriceHistoryResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetPriceHistoryResult, tlog, exc)
