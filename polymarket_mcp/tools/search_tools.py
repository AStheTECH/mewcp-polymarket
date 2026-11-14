"""Search group: search_events_and_markets"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.search import SearchEventsAndMarketsData, SearchEventsAndMarketsResult
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.search")


def register_search_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="search_events_and_markets",
        description=(
            "Runs a full-text search across Polymarket events and markets, optionally filtered by series, "
            "market type, start/closed time, status or combo-enabled markets. Returns the matching events, "
            "each with its associated markets nested under `markets` (IDs, slugs, titles, status flags, "
            "volumes, tags). Page through results with `page` and `limit`."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_events_and_markets(
        query: str | None = Field(default=None, description="The query to search for (free text). Omit to search without a text query."),
        limit: int | None = Field(default=None, description="The maximum number of results to return. Omit to use the API default."),
        series_ids: list[int] | None = Field(default=None, description="Filter by series IDs (integers, sent as repeated `seriesIds` values). Omit to not filter by series."),
        market_type: list[str] | None = Field(default=None, description="Filter by market types (sent as repeated `marketType` values). Omit to not filter by market type."),
        start_time_min: str | None = Field(default=None, description="Minimum start time filter: ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        start_time_max: str | None = Field(default=None, description="Maximum start time filter: ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        closed_time_min: str | None = Field(default=None, description="Minimum closed time filter: ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        closed_time_max: str | None = Field(default=None, description="Maximum closed time filter: ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        status: str | None = Field(default=None, description="Filter by status (free-form string; the provider lists no accepted values). Omit to not filter by status."),
        page: int | None = Field(default=None, description="Page number for pagination. Omit for the first page."),
        combo_enabled_only: bool | None = Field(default=None, description="Only return events with at least one combo-enabled market. Omit to include all events."),
    ) -> SearchEventsAndMarketsResult:
        tlog = ToolLogger(logger, "search_events_and_markets")
        params = {
            "query": query,
            "limit": limit,
            "seriesIds": series_ids,
            "marketType": market_type,
            "startTimeMin": start_time_min,
            "startTimeMax": start_time_max,
            "closedTimeMin": closed_time_min,
            "closedTimeMax": closed_time_max,
            "status": status,
            "page": page,
            "comboEnabledOnly": combo_enabled_only,
        }
        try:
            data, status_code, retry_after = service.api_request(
                "GET", "/v1/search", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status_code < 300:
                tlog.success()
                return SearchEventsAndMarketsResult(
                    success=True, statusCode=status_code, data=SearchEventsAndMarketsData(**data),
                )
            return _upstream_err(SearchEventsAndMarketsResult, tlog, status_code, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(SearchEventsAndMarketsResult, tlog, exc)
