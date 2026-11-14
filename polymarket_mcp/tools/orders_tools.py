"""Orders group: list_open_orders, get_order, preview_order, create_order, modify_order, cancel_order,
cancel_all_open_orders, close_position, create_multiple_orders, cancel_multiple_orders, modify_multiple_orders"""

import logging
from typing import Any, Literal
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.orders import (
    CancelAllOpenOrdersData,
    CancelAllOpenOrdersResult,
    CancelMultipleOrdersData,
    CancelMultipleOrdersResult,
    CancelOrderData,
    CancelOrderResult,
    ClosePositionData,
    ClosePositionResult,
    CreateMultipleOrdersData,
    CreateMultipleOrdersResult,
    CreateOrderData,
    CreateOrderResult,
    GetOrderData,
    GetOrderResult,
    ListOpenOrdersData,
    ListOpenOrdersResult,
    ModifyMultipleOrdersData,
    ModifyMultipleOrdersResult,
    ModifyOrderData,
    ModifyOrderResult,
    Order,
    PreviewOrderData,
    PreviewOrderResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.orders")

_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
_MAX_BATCH = 20

OrderType = Literal["ORDER_TYPE_LIMIT", "ORDER_TYPE_MARKET"]
TimeInForce = Literal[
    "TIME_IN_FORCE_DAY",
    "TIME_IN_FORCE_GOOD_TILL_CANCEL",
    "TIME_IN_FORCE_GOOD_TILL_DATE",
    "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL",
    "TIME_IN_FORCE_FILL_OR_KILL",
]
OrderIntent = Literal[
    "ORDER_INTENT_BUY_LONG", "ORDER_INTENT_SELL_LONG", "ORDER_INTENT_BUY_SHORT", "ORDER_INTENT_SELL_SHORT",
]
OutcomeSide = Literal["OUTCOME_SIDE_YES", "OUTCOME_SIDE_NO"]
OrderAction = Literal["ORDER_ACTION_BUY", "ORDER_ACTION_SELL"]
ManualOrderIndicator = Literal["MANUAL_ORDER_INDICATOR_MANUAL", "MANUAL_ORDER_INDICATOR_AUTOMATIC"]

_AMOUNT_KEYS = "keys `value` (decimal string, e.g. '0.55') and `currency` (e.g. 'USD')"
_D_MARKET_SLUG = "Unique market slug into which the order should be entered."
_D_TYPE = (
    "Order type: `ORDER_TYPE_LIMIT` requires `price`; `ORDER_TYPE_MARKET` executes at the best available price. "
    "Omit to use the exchange default."
)
_D_PRICE = f"Limit price per contract as an object with {_AMOUNT_KEYS}. Needed for limit orders; omit for market orders."
_D_QUANTITY = (
    "Order quantity in contracts. Decimal quantities are supported on markets whose minimumTradeQty is below 1. "
    "Omit when using `cash_order_qty`."
)
_D_TIF = (
    "Time in force: `TIME_IN_FORCE_DAY` expires at end of trading day; `TIME_IN_FORCE_GOOD_TILL_CANCEL` stays active "
    "until filled or canceled; `TIME_IN_FORCE_GOOD_TILL_DATE` expires at `good_till_time`; "
    "`TIME_IN_FORCE_IMMEDIATE_OR_CANCEL` fills immediately and cancels the rest; `TIME_IN_FORCE_FILL_OR_KILL` must fill "
    "entirely or is canceled. Omit to use the exchange default."
)
_D_PDI = (
    "If true, the order must rest on the book before matching (maker only) and is rejected if it would match "
    "immediately. Omit for no restriction."
)
_D_GTT = "Expiration time for `TIME_IN_FORCE_GOOD_TILL_DATE` orders. Omit for other time-in-force values."
_D_INTENT = (
    "Order intent: `ORDER_INTENT_BUY_LONG` = buy YES, `ORDER_INTENT_SELL_LONG` = sell YES, "
    "`ORDER_INTENT_BUY_SHORT` = buy NO, `ORDER_INTENT_SELL_SHORT` = sell NO. "
    "Set either this or `outcome_side` + `action`."
)
_D_OUTCOME_SIDE = (
    "Outcome side, set together with `action` as an alternative to `intent`; takes priority over `intent` if both "
    "are set. Omit when using `intent`."
)
_D_ACTION = "Order action, set together with `outcome_side` as an alternative to `intent`. Omit when using `intent`."
_D_CASH_QTY = (
    f"Order size in cash for market orders, instead of `quantity`, as an object with {_AMOUNT_KEYS}. "
    "Omit to size by `quantity`."
)
_D_MANUAL = "Whether the order was placed manually or automatically. Omit to leave unset."
_D_SYNC = (
    "If true, the call blocks until the order is filled, rejected, canceled or expired, up to `max_block_time` "
    "seconds, and the response includes its executions. Omit to return immediately."
)
_D_MAX_BLOCK = "Maximum seconds to block when `synchronous_execution` is true, as an integer string (e.g. '10')."
_D_SLIPPAGE = (
    "Slippage tolerance as an object with optional keys `currentPrice` (reference market price, an object with "
    f"{_AMOUNT_KEYS}), `bips` (int, basis points, 1 bip = 0.01%) and `ticks` (int, price ticks; takes priority over "
    "`bips`). Omit for no slippage limit."
)
_ORDER_FIELDS_DOC = (
    "`marketSlug` (str), `type` (ORDER_TYPE_LIMIT|ORDER_TYPE_MARKET), `price` ({value, currency}; needed for limit "
    "orders), `quantity` (float, contracts), `tif` (TIME_IN_FORCE_*), `participateDontInitiate` (bool), "
    "`goodTillTime` (str), `intent` (ORDER_INTENT_*), `outcomeSide` (OUTCOME_SIDE_YES|OUTCOME_SIDE_NO), "
    "`action` (ORDER_ACTION_BUY|ORDER_ACTION_SELL), `cashOrderQty` ({value, currency}), "
    "`manualOrderIndicator` (MANUAL_ORDER_INDICATOR_*), `synchronousExecution` (bool), `maxBlockTime` "
    "(integer string), `slippageTolerance` ({currentPrice, bips, ticks}). Each entry needs `marketSlug` and either "
    "`intent` or `outcomeSide` + `action`."
)


def _order_path(order_id: str, suffix: str = "") -> str:
    return f"/v1/order/{quote(order_id, safe='')}{suffix}"


def _no_body(data: Any) -> bool:
    # service returns {"error": <text>} when the body is empty or not JSON
    return not isinstance(data, dict) or set(data) <= {"error"}


def _compact(body: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in body.items() if v is not None}


def _amount_error(name: str, amount: dict | None) -> str | None:
    if amount is None:
        return None
    if not isinstance(amount, dict) or not amount.get("value") or not amount.get("currency"):
        return f"{name} must be an object with `value` and `currency`"
    return None


def _order_fields_error(
    intent: str | None, outcome_side: str | None, action: str | None,
    order_type: str | None, price: dict | None, cash_order_qty: dict | None,
    max_block_time: str | None, prefix: str = "",
) -> str | None:
    if intent is None and not (outcome_side and action):
        return f"{prefix}set either intent or both outcome_side and action"
    if order_type == "ORDER_TYPE_LIMIT" and price is None:
        return f"{prefix}ORDER_TYPE_LIMIT requires price"
    for name, amount in (("price", price), ("cash_order_qty", cash_order_qty)):
        msg = _amount_error(name, amount)
        if msg:
            return prefix + msg
    if max_block_time is not None and not str(max_block_time).isdigit():
        return f"{prefix}max_block_time must be a non-negative integer string"
    return None


def _batch_error(orders: list[dict], required: tuple[str, ...]) -> str | None:
    if len(orders) < 1 or len(orders) > _MAX_BATCH:
        return f"orders must contain 1–{_MAX_BATCH} entries"
    for i, entry in enumerate(orders):
        if not isinstance(entry, dict):
            return f"orders[{i}] must be an object"
        missing = [k for k in required if not entry.get(k)]
        if missing:
            return f"orders[{i}] is missing {', '.join(missing)}"
    return None


def _timeout(synchronous_execution: bool | None, max_block_time: str | None) -> tuple[int, int]:
    if synchronous_execution and max_block_time and str(max_block_time).isdigit():
        return (CONNECT_TIMEOUT, max(READ_TIMEOUT, int(max_block_time) + 10))
    return _TIMEOUT


def register_orders_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_open_orders",
        description=(
            "Lists the authenticated account's open orders, optionally limited to specific markets. "
            "Returns each order's `id`, market slug, intent, type, price, original/filled/remaining quantity, "
            "time in force and state; the `id` is the input for get_order, cancel_order, modify_order, "
            "cancel_multiple_orders and modify_multiple_orders."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_open_orders(
        slugs: list[str] | None = Field(
            default=None, description="Market slugs to filter by. Omit to list open orders in all markets.",
        ),
    ) -> ListOpenOrdersResult:
        tlog = ToolLogger(logger, "list_open_orders")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/orders/open", params={"slugs": slugs}, timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return ListOpenOrdersResult(success=True, statusCode=status, data=ListOpenOrdersData(**data))
            return _upstream_err(ListOpenOrdersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListOpenOrdersResult, tlog, exc)

    @mcp.tool(
        name="get_order",
        description=(
            "Gets one order by its exchange-assigned ID (from list_open_orders or create_order). "
            "Returns the order's market, intent, type, price, original/filled/remaining quantity, average fill "
            "price, commissions, time in force and current state."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_order(
        order_id: str = Field(description="Exchange-assigned order ID to retrieve."),
    ) -> GetOrderResult:
        tlog = ToolLogger(logger, "get_order")
        if not order_id.strip():
            return _err(GetOrderResult, tlog, "VALIDATION_ERROR", "order_id must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", _order_path(order_id), timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return GetOrderResult(success=True, statusCode=status, data=GetOrderData(**data))
            return _upstream_err(GetOrderResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetOrderResult, tlog, exc)

    @mcp.tool(
        name="preview_order",
        description=(
            "Previews an order without placing it: validates the same parameters create_order accepts and returns "
            "the order as it would be entered. Nothing is submitted to the exchange. "
            "Set either `intent` or `outcome_side` + `action`; `ORDER_TYPE_LIMIT` needs `price`."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def preview_order(
        market_slug: str = Field(description=_D_MARKET_SLUG),
        order_type: OrderType | None = Field(default=None, description=_D_TYPE),
        price: dict | None = Field(default=None, description=_D_PRICE),
        quantity: float | None = Field(default=None, description=_D_QUANTITY),
        tif: TimeInForce | None = Field(default=None, description=_D_TIF),
        participate_dont_initiate: bool | None = Field(default=None, description=_D_PDI),
        good_till_time: str | None = Field(default=None, description=_D_GTT),
        intent: OrderIntent | None = Field(default=None, description=_D_INTENT),
        outcome_side: OutcomeSide | None = Field(default=None, description=_D_OUTCOME_SIDE),
        action: OrderAction | None = Field(default=None, description=_D_ACTION),
        cash_order_qty: dict | None = Field(default=None, description=_D_CASH_QTY),
        manual_order_indicator: ManualOrderIndicator | None = Field(default=None, description=_D_MANUAL),
        synchronous_execution: bool | None = Field(default=None, description=_D_SYNC),
        max_block_time: str | None = Field(default=None, description=_D_MAX_BLOCK),
        slippage_tolerance: dict | None = Field(default=None, description=_D_SLIPPAGE),
    ) -> PreviewOrderResult:
        tlog = ToolLogger(logger, "preview_order")
        msg = _order_fields_error(intent, outcome_side, action, order_type, price, cash_order_qty, max_block_time)
        if msg:
            return _err(PreviewOrderResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            request = _compact({
                "marketSlug": market_slug, "type": order_type, "price": price, "quantity": quantity, "tif": tif,
                "participateDontInitiate": participate_dont_initiate, "goodTillTime": good_till_time,
                "intent": intent, "outcomeSide": outcome_side, "action": action, "cashOrderQty": cash_order_qty,
                "manualOrderIndicator": manual_order_indicator, "synchronousExecution": synchronous_execution,
                "maxBlockTime": max_block_time, "slippageTolerance": slippage_tolerance,
            })
            data, status, retry_after = service.api_request(
                "POST", "/v1/order/preview", body={"request": request}, timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return PreviewOrderResult(success=True, statusCode=status, data=PreviewOrderData(**data))
            return _upstream_err(PreviewOrderResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(PreviewOrderResult, tlog, exc)

    @mcp.tool(
        name="create_order",
        description=(
            "Places a real order on the exchange for the authenticated account to buy or sell YES/NO contracts in "
            "one market; it can fill immediately and commits account funds, so confirm the market, intent, price "
            "and size with the user first (use preview_order to validate without placing anything). "
            "Returns the new order `id` (input for get_order, cancel_order and modify_order) and, when "
            "`synchronous_execution` is true, its executions. Set either `intent` or `outcome_side` + `action`; "
            "`ORDER_TYPE_LIMIT` needs `price`. Orders not processed within 5 seconds are rejected with "
            "`Order Processing Max Delay Exceeded`, a transient latency reject (not a rate limit) after which the "
            "order may be resubmitted."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_order(
        market_slug: str = Field(description=_D_MARKET_SLUG),
        order_type: OrderType | None = Field(default=None, description=_D_TYPE),
        price: dict | None = Field(default=None, description=_D_PRICE),
        quantity: float | None = Field(default=None, description=_D_QUANTITY),
        tif: TimeInForce | None = Field(default=None, description=_D_TIF),
        participate_dont_initiate: bool | None = Field(default=None, description=_D_PDI),
        good_till_time: str | None = Field(default=None, description=_D_GTT),
        intent: OrderIntent | None = Field(default=None, description=_D_INTENT),
        outcome_side: OutcomeSide | None = Field(default=None, description=_D_OUTCOME_SIDE),
        action: OrderAction | None = Field(default=None, description=_D_ACTION),
        cash_order_qty: dict | None = Field(default=None, description=_D_CASH_QTY),
        manual_order_indicator: ManualOrderIndicator | None = Field(default=None, description=_D_MANUAL),
        synchronous_execution: bool | None = Field(default=None, description=_D_SYNC),
        max_block_time: str | None = Field(default=None, description=_D_MAX_BLOCK),
        slippage_tolerance: dict | None = Field(default=None, description=_D_SLIPPAGE),
    ) -> CreateOrderResult:
        tlog = ToolLogger(logger, "create_order")
        msg = _order_fields_error(intent, outcome_side, action, order_type, price, cash_order_qty, max_block_time)
        if msg:
            return _err(CreateOrderResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            body = _compact({
                "marketSlug": market_slug, "type": order_type, "price": price, "quantity": quantity, "tif": tif,
                "participateDontInitiate": participate_dont_initiate, "goodTillTime": good_till_time,
                "intent": intent, "outcomeSide": outcome_side, "action": action, "cashOrderQty": cash_order_qty,
                "manualOrderIndicator": manual_order_indicator, "synchronousExecution": synchronous_execution,
                "maxBlockTime": max_block_time, "slippageTolerance": slippage_tolerance,
            })
            data, status, retry_after = service.api_request(
                "POST", "/v1/orders", body=body,
                timeout=_timeout(synchronous_execution, max_block_time), authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return CreateOrderResult(success=True, statusCode=status, data=CreateOrderData(**data))
            return _upstream_err(CreateOrderResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreateOrderResult, tlog, exc)

    @mcp.tool(
        name="modify_order",
        description=(
            "Modifies an existing open order (ID from list_open_orders) — it can overwrite the price, quantity, "
            "time in force, good-till time and maker-only flag; the exchange applies it as a cancel-replace. "
            "Only fields you provide are changed — others keep their current value. NOTE: this overwrites the "
            "current order values — the original state is not stored by the API after the call. The response "
            "includes both the before and after state (each read via get_order) so you have a full record of what "
            "changed; `after` is read immediately and may still show ORDER_STATE_PENDING_REPLACE. Modifications "
            "not processed within 5 seconds are rejected with `Order Processing Max Delay Exceeded`, a transient "
            "latency reject after which the request may be resubmitted."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def modify_order(
        order_id: str = Field(description="Exchange-assigned order ID to modify."),
        market_slug: str | None = Field(default=None, description="Market slug of the order being modified. Omit to leave unset."),
        price: dict | None = Field(
            default=None, description=f"New limit price as an object with {_AMOUNT_KEYS}. Omit to keep the current price.",
        ),
        quantity: float | None = Field(
            default=None,
            description="New order quantity in contracts (decimals allowed on markets whose minimumTradeQty is below "
                        "1). Omit to keep the current quantity.",
        ),
        tif: TimeInForce | None = Field(
            default=None, description=_D_TIF.replace("Omit to use the exchange default.", "Omit to keep the current value."),
        ),
        participate_dont_initiate: bool | None = Field(
            default=None, description="If true, the order must rest on the book before matching (maker only). Omit to keep the current value.",
        ),
        good_till_time: str | None = Field(
            default=None, description="New expiration time for `TIME_IN_FORCE_GOOD_TILL_DATE` orders. Omit to keep the current value.",
        ),
    ) -> ModifyOrderResult:
        tlog = ToolLogger(logger, "modify_order")
        if not order_id.strip():
            return _err(ModifyOrderResult, tlog, "VALIDATION_ERROR", "order_id must not be empty", 400)
        msg = _amount_error("price", price)
        if msg:
            return _err(ModifyOrderResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", _order_path(order_id), timeout=_TIMEOUT, authenticated=True,
            )
            if not 200 <= status < 300:
                return _upstream_err(ModifyOrderResult, tlog, status, data, retry_after)
            before = Order(**(data.get("order") or {}))

            body = _compact({
                "marketSlug": market_slug, "price": price, "quantity": quantity, "tif": tif,
                "participateDontInitiate": participate_dont_initiate, "goodTillTime": good_till_time,
            })
            data, modify_status, retry_after = service.api_request(
                "POST", _order_path(order_id, "/modify"), body=body, timeout=_TIMEOUT, authenticated=True,
            )
            if not 200 <= modify_status < 300:
                return _upstream_err(ModifyOrderResult, tlog, modify_status, data, retry_after)

            after = None
            try:
                data, status, _ = service.api_request(
                    "GET", _order_path(order_id), timeout=_TIMEOUT, authenticated=True,
                )
                if 200 <= status < 300:
                    after = Order(**(data.get("order") or {}))
            except Exception:
                logger.warning("tool=modify_order status=after_read_failed")
            tlog.success()
            return ModifyOrderResult(
                success=True, statusCode=modify_status, data=ModifyOrderData(before=before, after=after),
            )
        except Exception as exc:
            return _handle_request_exc(ModifyOrderResult, tlog, exc)

    @mcp.tool(
        name="cancel_order",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Cancels one open order by its exchange-assigned ID (from list_open_orders), removing its remaining "
            "unfilled quantity from the book. This action is irreversible — a canceled order cannot be restored "
            "and must be placed again with create_order. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly which order (market, side, price, quantity) will be canceled and "
            "that it is permanent, and wait for their explicit written confirmation before proceeding. "
            "Returns the canceled order ID (the API returns an empty body on success). Pure cancels are never "
            "rejected by the exchange's 5-second latency stopgap."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def cancel_order(
        order_id: str = Field(description="Exchange-assigned order ID to cancel."),
        market_slug: str | None = Field(
            default=None, description="Market slug the order belongs to. Omit to send the cancel without it.",
        ),
    ) -> CancelOrderResult:
        tlog = ToolLogger(logger, "cancel_order")
        if not order_id.strip():
            return _err(CancelOrderResult, tlog, "VALIDATION_ERROR", "order_id must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "POST", _order_path(order_id, "/cancel"), body=_compact({"marketSlug": market_slug}),
                timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                extra = {} if _no_body(data) else {k: v for k, v in data.items() if k != "orderId"}
                tlog.success()
                return CancelOrderResult(
                    success=True, statusCode=status, data=CancelOrderData(orderId=order_id, **extra),
                )
            return _upstream_err(CancelOrderResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CancelOrderResult, tlog, exc)

    @mcp.tool(
        name="cancel_all_open_orders",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Cancels ALL open orders of the authenticated account in the markets listed in `slugs`. "
            "If `slugs` is omitted or empty, it cancels EVERY open order in EVERY market on the account. "
            "This action is irreversible — canceled orders cannot be restored and must be placed again with "
            "create_order. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly which orders will be canceled (run list_open_orders with the "
            "same `slugs` to show them) and that it is permanent, and wait for their explicit written confirmation "
            "before proceeding. Returns `canceledOrderIds`."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def cancel_all_open_orders(
        slugs: list[str] | None = Field(
            default=None,
            description="Market slugs whose open orders to cancel. Omit or pass an empty list to cancel every open "
                        "order in all markets.",
        ),
    ) -> CancelAllOpenOrdersResult:
        tlog = ToolLogger(logger, "cancel_all_open_orders")
        try:
            data, status, retry_after = service.api_request(
                "POST", "/v1/orders/open/cancel", body=_compact({"slugs": slugs or None}),
                timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                payload = {} if _no_body(data) else data
                return CancelAllOpenOrdersResult(
                    success=True, statusCode=status, data=CancelAllOpenOrdersData(**payload),
                )
            return _upstream_err(CancelAllOpenOrdersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CancelAllOpenOrdersResult, tlog, exc)

    @mcp.tool(
        name="close_position",
        description=(
            "Places a market sell order for the ENTIRE position the authenticated account holds in one market "
            "(YES or NO contracts), exiting it at the best available price; confirm with the user first. It cannot "
            "sell part of a position or set a limit price — use create_order with ORDER_INTENT_SELL_LONG or "
            "ORDER_INTENT_SELL_SHORT for that. Returns the close order `id` and, when `synchronous_execution` is "
            "true, its executions. Orders not processed within 5 seconds are rejected with "
            "`Order Processing Max Delay Exceeded`, a transient latency reject after which the request may be "
            "resubmitted."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def close_position(
        market_slug: str = Field(description="Market slug of the position to close."),
        manual_order_indicator: ManualOrderIndicator | None = Field(default=None, description=_D_MANUAL),
        synchronous_execution: bool | None = Field(default=None, description=_D_SYNC),
        max_block_time: str | None = Field(default=None, description=_D_MAX_BLOCK),
        slippage_tolerance: dict | None = Field(default=None, description=_D_SLIPPAGE),
    ) -> ClosePositionResult:
        tlog = ToolLogger(logger, "close_position")
        if not market_slug.strip():
            return _err(ClosePositionResult, tlog, "VALIDATION_ERROR", "market_slug must not be empty", 400)
        if max_block_time is not None and not str(max_block_time).isdigit():
            return _err(ClosePositionResult, tlog, "VALIDATION_ERROR",
                        "max_block_time must be a non-negative integer string", 400)
        try:
            body = _compact({
                "marketSlug": market_slug, "manualOrderIndicator": manual_order_indicator,
                "synchronousExecution": synchronous_execution, "maxBlockTime": max_block_time,
                "slippageTolerance": slippage_tolerance,
            })
            data, status, retry_after = service.api_request(
                "POST", "/v1/order/close-position", body=body,
                timeout=_timeout(synchronous_execution, max_block_time), authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return ClosePositionResult(success=True, statusCode=status, data=ClosePositionData(**data))
            return _upstream_err(ClosePositionResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ClosePositionResult, tlog, exc)

    @mcp.tool(
        name="create_multiple_orders",
        description=(
            "Places 1–20 real orders on the exchange in one request, each taking the same fields as create_order; "
            "they can fill immediately and commit account funds, so confirm every order with the user first. "
            "Returns `createdOrderIds` in request order — these only confirm submission: per-order acceptance, "
            "fills and rejects are not in this response, so check each with get_order. If any entry fails "
            "request-shape validation, the whole batch is rejected before reaching the exchange."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_multiple_orders(
        orders: list[dict] = Field(
            description=f"Orders to place (1–20). Each entry is an object with wire-name keys: {_ORDER_FIELDS_DOC}",
        ),
    ) -> CreateMultipleOrdersResult:
        tlog = ToolLogger(logger, "create_multiple_orders")
        msg = _batch_error(orders, ("marketSlug",))
        if not msg:
            for i, entry in enumerate(orders):
                msg = _order_fields_error(
                    entry.get("intent"), entry.get("outcomeSide"), entry.get("action"), entry.get("type"),
                    entry.get("price"), entry.get("cashOrderQty"), entry.get("maxBlockTime"), prefix=f"orders[{i}]: ",
                )
                if msg:
                    break
        if msg:
            return _err(CreateMultipleOrdersResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            data, status, retry_after = service.api_request(
                "POST", "/v1/orders/batched", body={"orders": [_compact(o) for o in orders]},
                timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                return CreateMultipleOrdersResult(
                    success=True, statusCode=status, data=CreateMultipleOrdersData(**data),
                )
            return _upstream_err(CreateMultipleOrdersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreateMultipleOrdersResult, tlog, exc)

    @mcp.tool(
        name="cancel_multiple_orders",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Cancels the 1–20 listed open orders in one request, removing their remaining unfilled quantity from "
            "the book. This action is irreversible — canceled orders cannot be restored and must be placed again "
            "with create_order. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly which orders will be canceled and that it is permanent, and wait "
            "for their explicit written confirmation before proceeding. "
            "Returns `canceledOrderIds`, which only echoes the request — the exchange may silently ignore unknown "
            "order IDs, so verify with list_open_orders. If any entry fails request-shape validation, the whole "
            "batch is rejected before reaching the exchange."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def cancel_multiple_orders(
        orders: list[dict] = Field(
            description="Orders to cancel (1–20). Each entry is an object with `orderId` (exchange-assigned order "
                        "ID) and `marketSlug` (market slug the order belongs to).",
        ),
    ) -> CancelMultipleOrdersResult:
        tlog = ToolLogger(logger, "cancel_multiple_orders")
        msg = _batch_error(orders, ("orderId", "marketSlug"))
        if msg:
            return _err(CancelMultipleOrdersResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            data, status, retry_after = service.api_request(
                "POST", "/v1/orders/batched/cancel", body={"orders": [_compact(o) for o in orders]},
                timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                payload = {} if _no_body(data) else data
                return CancelMultipleOrdersResult(
                    success=True, statusCode=status, data=CancelMultipleOrdersData(**payload),
                )
            return _upstream_err(CancelMultipleOrdersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CancelMultipleOrdersResult, tlog, exc)

    @mcp.tool(
        name="modify_multiple_orders",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Modifies the 1–20 listed open orders in one request, overwriting each order's price, quantity, time in "
            "force, good-till time or maker-only flag as given; each entry is sent to the exchange as a "
            "cancel-replace. The previous order values are not returned and cannot be recovered from this call. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, summarise to the user exactly which orders change and their new values, and wait for "
            "their explicit written confirmation before proceeding. "
            "Returns `modifiedOrderIds`, which only echoes the request — the exchange may silently ignore unknown "
            "order IDs, so verify with get_order. If any entry fails request-shape validation, the whole batch is "
            "rejected before reaching the exchange."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def modify_multiple_orders(
        orders: list[dict] = Field(
            description="Orders to modify (1–20). Each entry is an object with `orderId` (exchange-assigned order "
                        "ID), `marketSlug` (market slug the order belongs to) and any of `price` ({value: decimal "
                        "string, currency: e.g. 'USD'}), `quantity` (float, contracts), `tif` (TIME_IN_FORCE_*), "
                        "`participateDontInitiate` (bool, maker only) and `goodTillTime` (str, for GTD orders).",
        ),
    ) -> ModifyMultipleOrdersResult:
        tlog = ToolLogger(logger, "modify_multiple_orders")
        msg = _batch_error(orders, ("orderId", "marketSlug"))
        if not msg:
            for i, entry in enumerate(orders):
                msg = _amount_error(f"orders[{i}].price", entry.get("price"))
                if msg:
                    break
        if msg:
            return _err(ModifyMultipleOrdersResult, tlog, "VALIDATION_ERROR", msg, 400)
        try:
            data, status, retry_after = service.api_request(
                "POST", "/v1/orders/batched/modify", body={"orders": [_compact(o) for o in orders]},
                timeout=_TIMEOUT, authenticated=True,
            )
            if 200 <= status < 300:
                tlog.success()
                payload = {} if _no_body(data) else data
                return ModifyMultipleOrdersResult(
                    success=True, statusCode=status, data=ModifyMultipleOrdersData(**payload),
                )
            return _upstream_err(ModifyMultipleOrdersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ModifyMultipleOrdersResult, tlog, exc)
