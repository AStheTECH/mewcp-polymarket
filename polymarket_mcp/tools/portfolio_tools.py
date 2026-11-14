"""Portfolio group: list_positions, list_activities."""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.portfolio import (
    ListActivitiesData,
    ListActivitiesResult,
    ListPositionsData,
    ListPositionsResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.portfolio")

ActivityType = Literal[
    "ACTIVITY_TYPE_TRADE",
    "ACTIVITY_TYPE_POSITION_RESOLUTION",
    "ACTIVITY_TYPE_ACCOUNT_DEPOSIT",
    "ACTIVITY_TYPE_ACCOUNT_ADVANCED_DEPOSIT",
    "ACTIVITY_TYPE_ACCOUNT_WITHDRAWAL",
    "ACTIVITY_TYPE_REFERRAL_BONUS",
    "ACTIVITY_TYPE_TRANSFER",
    "ACTIVITY_TYPE_TAKER_FEE_REBATE",
    "ACTIVITY_TYPE_LIQUIDITY_PROGRAM",
]


def register_portfolio_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_positions",
        description=(
            "Lists the user's trading positions across all markets, or only the position for one market "
            "when `market` is given. Returns a map of market slug to position (decimal-string quantities, "
            "cost basis, realized PnL, unrealized cash value, market metadata) plus `nextCursor` and `eof` "
            "for cursor pagination. Prefer the *Decimal quantity fields; the whole-number ones are deprecated."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_positions(
        market: str | None = Field(default=None, description="Market slug to return only that market's position (e.g. `will-team-a-win`). Omit for all markets."),
        limit: int | None = Field(default=None, description="Maximum positions per page. Omit for the server default of 100."),
        cursor: str | None = Field(default=None, description="`nextCursor` from a previous response, to fetch the next page. Omit for the first page."),
    ) -> ListPositionsResult:
        tlog = ToolLogger(logger, "list_positions")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/portfolio/positions",
                params={"market": market, "limit": limit, "cursor": cursor},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=True,
            )
            if 200 <= status < 300:
                result = ListPositionsResult(success=True, statusCode=status,
                                             data=ListPositionsData.model_validate(data))
                tlog.success()
                return result
            return _upstream_err(ListPositionsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListPositionsResult, tlog, exc)

    @mcp.tool(
        name="list_activities",
        description=(
            "Lists the user's account activity history: trades, position resolutions (market settlements) "
            "and account balance changes such as deposits, withdrawals, transfers, referral bonuses, fee "
            "rebates and liquidity-program payouts. Each activity carries a `type` plus the matching "
            "`trade`, `positionResolution` or `accountBalanceChange` object; results are newest first by "
            "default and paginate with `nextCursor` / `eof`."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_activities(
        limit: int | None = Field(default=None, description="Maximum activities per page. Omit for the server default of 100."),
        cursor: str | None = Field(default=None, description="`nextCursor` from a previous response, to fetch the next page. Omit for the first page."),
        marketSlug: str | None = Field(default=None, description="Market slug to return only trades and resolutions for that market (e.g. `will-team-a-win`). Omit for all markets."),
        types: list[ActivityType] | None = Field(default=None, description="Activity types to include; only activities of these types are returned. Omit for all types."),
        sortOrder: Literal["SORT_ORDER_DESCENDING", "SORT_ORDER_ASCENDING"] | None = Field(default=None, description="Sort by timestamp: SORT_ORDER_DESCENDING (newest first) or SORT_ORDER_ASCENDING (oldest first). Omit for newest first."),
    ) -> ListActivitiesResult:
        tlog = ToolLogger(logger, "list_activities")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/portfolio/activities",
                params={
                    "limit": limit,
                    "cursor": cursor,
                    "marketSlug": marketSlug,
                    "types": types,
                    "sortOrder": sortOrder,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=True,
            )
            if 200 <= status < 300:
                result = ListActivitiesResult(success=True, statusCode=status,
                                              data=ListActivitiesData.model_validate(data))
                tlog.success()
                return result
            return _upstream_err(ListActivitiesResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListActivitiesResult, tlog, exc)
