"""Incentives group: list_incentive_programs, list_incentive_earnings."""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.incentives import (
    ListIncentiveEarningsData,
    ListIncentiveEarningsResult,
    ListIncentiveProgramsData,
    ListIncentiveProgramsResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.incentives")

InstrumentState = Literal[
    "INSTRUMENT_STATE_OPEN",
    "INSTRUMENT_STATE_PREOPEN",
    "INSTRUMENT_STATE_SUSPENDED",
    "INSTRUMENT_STATE_EXPIRED",
    "INSTRUMENT_STATE_TERMINATED",
    "INSTRUMENT_STATE_HALTED",
    "INSTRUMENT_STATE_MATCH_AND_CLOSE_AUCTION",
    "INSTRUMENT_STATE_PENDING",
]


def register_incentives_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_incentive_programs",
        description=(
            "Lists active and historical incentive programs grouped by market. Returns each market's slug, "
            "instrument state, category and its time periods (program ID and type, start/end, reward pool, "
            "status, liquidity targets such as targetSize and maxSpread), plus `nextPageToken` for paging; "
            "`page_size` counts markets, not time periods."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_incentive_programs(
        page_size: int | None = Field(default=None, description="Number of markets per page. Omit for the server default."),
        page_token: str | None = Field(default=None, description="`nextPageToken` from a previous response, to fetch the next page. Omit for the first page."),
        symbols: list[str] | None = Field(default=None, description="Market symbols to return programs for. Omit for all markets."),
        order_by: str | None = Field(default=None, description="Sort field. Omit for the server default `created_at`."),
        order_direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction. Omit for the server default `desc`."),
        statuses: list[Literal["active", "closed", "pending"]] | None = Field(default=None, description="Program statuses to include. Omit for all statuses."),
        program_type: str | None = Field(default=None, description="Program type to filter by, such as `liquidityProgram` or `volumeProgram`. Omit for all types."),
        query: str | None = Field(default=None, description="Case-insensitive substring to match against market slugs. Omit for no slug filter."),
        instrument_states: list[InstrumentState] | None = Field(default=None, description="Instrument lifecycle states to include. Omit for all states."),
        category: str | None = Field(default=None, description="Exact event category to filter by. Omit for all categories."),
        subcategory: str | None = Field(default=None, description="Exact event subcategory to filter by. Omit for all subcategories."),
    ) -> ListIncentiveProgramsResult:
        tlog = ToolLogger(logger, "list_incentive_programs")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/incentives",
                params={
                    "page_size": page_size,
                    "page_token": page_token,
                    "symbols": symbols,
                    "order_by": order_by,
                    "order_direction": order_direction,
                    "statuses": statuses,
                    "program_type": program_type,
                    "query": query,
                    "instrument_states": instrument_states,
                    "category": category,
                    "subcategory": subcategory,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=True,
            )
            if 200 <= status < 300:
                result = ListIncentiveProgramsResult(success=True, statusCode=status,
                                                     data=ListIncentiveProgramsData.model_validate(data))
                tlog.success()
                return result
            return _upstream_err(ListIncentiveProgramsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListIncentiveProgramsResult, tlog, exc)

    @mcp.tool(
        name="list_incentive_earnings",
        description=(
            "Lists the authenticated user's incentive rewards, where each entry sums all payouts for one "
            "market on one Eastern Time date. Returns reward amount, program type, market slug, date and "
            "status; by default covers the program launch date through today."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_incentive_earnings(
        start_date: str | None = Field(default=None, description="Start date in `YYYY-MM-DD` format. Omit to start from the program launch date."),
        end_date: str | None = Field(default=None, description="End date in `YYYY-MM-DD` format. Omit to include through today."),
        market_slug: str | None = Field(default=None, description="Market slug to filter by. Omit for all markets."),
        program_type: str | None = Field(default=None, description="Program type to filter by (e.g. `liquidityProgram`). Omit for all types."),
    ) -> ListIncentiveEarningsResult:
        tlog = ToolLogger(logger, "list_incentive_earnings")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/incentives/earnings",
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "market_slug": market_slug,
                    "program_type": program_type,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=True,
            )
            if 200 <= status < 300:
                result = ListIncentiveEarningsResult(success=True, statusCode=status,
                                                     data=ListIncentiveEarningsData.model_validate(data))
                tlog.success()
                return result
            return _upstream_err(ListIncentiveEarningsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListIncentiveEarningsResult, tlog, exc)
