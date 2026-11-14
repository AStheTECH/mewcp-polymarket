"""Asset prices group: get_asset_price_history"""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.asset_prices import GetAssetPriceHistoryData, GetAssetPriceHistoryResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.asset_prices")

_MAX_ASSETS = 10


def register_asset_prices_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_asset_price_history",
        description=(
            "Gets reference price history for crypto, gold and silver price markets as a dense, ascending "
            "OHLC candle series per requested asset between `from` and `to`, one candle per bucket. Returns "
            "one series per distinct asset with its currency, effective window and candles (decimal-string "
            "prices); buckets with no ticks are gap-filled (close carried forward, tickCount 0). The window is "
            "clamped, not rejected: `from` is raised so a series holds at most 3600 candles (an hour at 1S, "
            "60 hours at 1M, 150 days at 1H), and the effective bounds are echoed on each series. Series order "
            "is not guaranteed; each series carries its `asset` field. An unknown symbol, or an asset whose markets "
            "are not available yet, fails the whole request with 404."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_asset_price_history(
        from_: int = Field(description="Unix-seconds start of the window. Aligned down to the bucket, and raised when the window would exceed 3600 candles; the effective start is echoed in the series' `from`."),
        bucket: Literal[
            "ASSET_PRICE_BUCKET_1S",
            "ASSET_PRICE_BUCKET_5S",
            "ASSET_PRICE_BUCKET_15S",
            "ASSET_PRICE_BUCKET_1M",
            "ASSET_PRICE_BUCKET_5M",
            "ASSET_PRICE_BUCKET_15M",
            "ASSET_PRICE_BUCKET_1H",
            "ASSET_PRICE_BUCKET_1D",
        ] = Field(description="Candle width."),
        assets: list[str] | None = Field(default=None, description="Assets in canonical <class>:<symbol> form, e.g. crypto:btc, commodity:gold or commodity:silver. At most 10; duplicates are deduped server-side. Optional."),
        to: int | None = Field(default=None, description="Unix-seconds end of the window. 0 or a future value means now. The in-progress bucket is included. A past value is aligned up to 10 s for sub-minute buckets, or to one bucket otherwise; the effective end is echoed in the series' `to`. Omit to leave unset."),
    ) -> GetAssetPriceHistoryResult:
        tlog = ToolLogger(logger, "get_asset_price_history")

        if assets is not None and len(assets) > _MAX_ASSETS:
            return _err(GetAssetPriceHistoryResult, tlog, "VALIDATION_ERROR",
                        f"assets accepts at most {_MAX_ASSETS} entries", 400)

        params = {"assets": assets, "from": from_, "to": to, "bucket": bucket}
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/asset-prices/history", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetAssetPriceHistoryResult(
                    success=True, statusCode=status, data=GetAssetPriceHistoryData(**data),
                )
            return _upstream_err(GetAssetPriceHistoryResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetAssetPriceHistoryResult, tlog, exc)
