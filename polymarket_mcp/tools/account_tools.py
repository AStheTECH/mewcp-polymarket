"""Account group: get_account_balances."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.account import GetAccountBalancesData, GetAccountBalancesResult
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.account")


def register_account_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_account_balances",
        description=(
            "Gets the user's current account balances, one entry per currency. Returns current fiat "
            "balance, buying power (capital available to trade after security valuations and open "
            "orders), asset notional and available collateral, pending credits, open-order and "
            "unsettled-fund totals, margin requirement, balance reservations and any pending withdrawals."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_account_balances() -> GetAccountBalancesResult:
        tlog = ToolLogger(logger, "get_account_balances")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/account/balances",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=True,
            )
            if 200 <= status < 300:
                result = GetAccountBalancesResult(success=True, statusCode=status,
                                                  data=GetAccountBalancesData.model_validate(data))
                tlog.success()
                return result
            return _upstream_err(GetAccountBalancesResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetAccountBalancesResult, tlog, exc)
