"""Orders group schemas."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class Amount(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: str | None = Field(default=None, description="Amount as a decimal string (e.g. '0.55').")
    currency: str | None = Field(default=None, description="Currency code (e.g. 'USD').")


class Team(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    abbreviation: str | None = None
    league: str | None = None
    record: str | None = Field(default=None, description="Team record (wins-losses).")
    logo: str | None = None
    alias: str | None = None
    safeName: str | None = Field(default=None, description="URL-safe team name.")
    homeIcon: str | None = None
    awayIcon: str | None = None
    colorPrimary: str | None = Field(default=None, description="Primary team color (hex).")
    ordering: str | None = Field(default=None, description="Display ordering.")
    ranking: str | None = None
    conference: str | None = None


class MarketMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str | None = None
    icon: str | None = None
    title: str | None = None
    outcome: str | None = Field(default=None, description="Market outcome description.")
    eventSlug: str | None = Field(default=None, description="Parent event slug.")
    teamId: int | None = Field(default=None, description="Deprecated; use `team`.")
    team: Team | None = None


class Order(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="Exchange-assigned order ID.")
    marketSlug: str | None = None
    side: str | None = Field(default=None, description="ORDER_SIDE_BUY or ORDER_SIDE_SELL.")
    type: str | None = Field(default=None, description="ORDER_TYPE_LIMIT or ORDER_TYPE_MARKET.")
    price: Amount | None = None
    quantity: float | None = Field(default=None, description="Original order quantity in contracts.")
    cumQuantity: float | None = Field(default=None, description="Cumulative filled quantity in contracts.")
    leavesQuantity: float | None = Field(default=None, description="Remaining unfilled quantity in contracts.")
    tif: str | None = Field(
        default=None,
        description="TIME_IN_FORCE_DAY, TIME_IN_FORCE_GOOD_TILL_CANCEL, TIME_IN_FORCE_GOOD_TILL_DATE, "
                    "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL or TIME_IN_FORCE_FILL_OR_KILL.",
    )
    goodTillTime: str | None = Field(default=None, description="Expiration time for GTD orders.")
    intent: str | None = Field(
        default=None,
        description="ORDER_INTENT_BUY_LONG (buy YES), ORDER_INTENT_SELL_LONG (sell YES), "
                    "ORDER_INTENT_BUY_SHORT (buy NO) or ORDER_INTENT_SELL_SHORT (sell NO).",
    )
    marketMetadata: MarketMetadata | None = None
    state: str | None = Field(
        default=None,
        description="ORDER_STATE_NEW, ORDER_STATE_PARTIALLY_FILLED, ORDER_STATE_FILLED, ORDER_STATE_CANCELED, "
                    "ORDER_STATE_REPLACED, ORDER_STATE_REJECTED, ORDER_STATE_EXPIRED, ORDER_STATE_PENDING_NEW, "
                    "ORDER_STATE_PENDING_REPLACE, ORDER_STATE_PENDING_CANCEL or ORDER_STATE_PENDING_RISK.",
    )
    commissionNotionalTotalCollected: Amount | None = Field(
        default=None, description="Total notional value of all commissions collected on this order.",
    )
    commissionsBasisPoints: str | None = Field(default=None, description="Commission rate in basis points.")
    makerCommissionsBasisPoints: str | None = Field(default=None, description="Maker commission rate in basis points.")
    avgPx: Amount | None = Field(default=None, description="Average fill price.")
    cashOrderQty: Amount | None = Field(default=None, description="Total cash order quantity for market orders.")
    insertTime: str | None = Field(default=None, description="Time the order was inserted into the book or replaced.")
    createTime: str | None = None
    outcomeSide: str | None = Field(default=None, description="OUTCOME_SIDE_YES or OUTCOME_SIDE_NO.")
    action: str | None = Field(default=None, description="ORDER_ACTION_BUY or ORDER_ACTION_SELL.")


class LegPrice(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketSlug: str | None = None
    anchor: bool | None = None
    px: Amount | None = None
    qty: str | None = None
    side: str | None = Field(default=None, description="ORDER_SIDE_BUY or ORDER_SIDE_SELL.")
    referencePx: str | None = None


class Execution(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="Exchange-assigned execution ID.")
    order: Order | None = Field(default=None, description="The order at the time of this execution.")
    lastShares: str | None = Field(default=None, description="Last fill quantity as a decimal string.")
    lastPx: Amount | None = Field(default=None, description="Price of this execution.")
    type: str | None = Field(
        default=None,
        description="EXECUTION_TYPE_NEW, EXECUTION_TYPE_PARTIAL_FILL, EXECUTION_TYPE_FILL, EXECUTION_TYPE_CANCELED, "
                    "EXECUTION_TYPE_REPLACE, EXECUTION_TYPE_REJECTED, EXECUTION_TYPE_EXPIRED or "
                    "EXECUTION_TYPE_DONE_FOR_DAY.",
    )
    text: str | None = None
    orderRejectReason: str | None = Field(default=None, description="Rejection reason if the execution type is rejected.")
    transactTime: str | None = None
    legPrices: list[LegPrice] = []
    tradeId: str | None = Field(default=None, description="Trade ID if this is a fill.")
    aggressor: bool | None = Field(default=None, description="True if this order was the taker, false if the maker.")
    commissionNotionalCollected: Amount | None = None
    unsolicitedCancelReason: str | None = None
    traceId: str | None = None
    commissionSpreadPx: Amount | None = None
    transactTradeDate: str | None = None


# list_open_orders
class ListOpenOrdersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    orders: list[Order] = []


class ListOpenOrdersResult(ToolResult):
    data: ListOpenOrdersData | None = None


# get_order
class GetOrderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    order: Order | None = None


class GetOrderResult(ToolResult):
    data: GetOrderData | None = None


# preview_order
class PreviewOrderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    order: Order | None = None


class PreviewOrderResult(ToolResult):
    data: PreviewOrderData | None = None


# create_order
class CreateOrderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="Exchange-assigned ID of the created order.")
    executions: list[Execution] = Field(
        default=[], description="Executions; populated only when synchronous execution was requested.",
    )


class CreateOrderResult(ToolResult):
    data: CreateOrderData | None = None


# modify_order
class ModifyOrderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: Order
    after: Order | None = Field(default=None, description="Order re-read after the modify; null if that read failed.")


class ModifyOrderResult(ToolResult):
    data: ModifyOrderData | None = None


# cancel_order
class CancelOrderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    orderId: str


class CancelOrderResult(ToolResult):
    data: CancelOrderData | None = None


# cancel_all_open_orders
class CancelAllOpenOrdersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    canceledOrderIds: list[str] = []


class CancelAllOpenOrdersResult(ToolResult):
    data: CancelAllOpenOrdersData | None = None


# close_position
class ClosePositionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="Exchange-assigned ID of the close order.")
    executions: list[Execution] = Field(
        default=[], description="Executions; populated only when synchronous execution was requested.",
    )


class ClosePositionResult(ToolResult):
    data: ClosePositionData | None = None


# create_multiple_orders
class CreateMultipleOrdersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    createdOrderIds: list[str] = Field(
        default=[], description="IDs of the submitted orders, in request order; not a confirmation of acceptance.",
    )


class CreateMultipleOrdersResult(ToolResult):
    data: CreateMultipleOrdersData | None = None


# cancel_multiple_orders
class CancelMultipleOrdersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    canceledOrderIds: list[str] = Field(
        default=[], description="Echo of the requested order IDs; not a confirmation of cancellation.",
    )


class CancelMultipleOrdersResult(ToolResult):
    data: CancelMultipleOrdersData | None = None


# modify_multiple_orders
class ModifyMultipleOrdersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    modifiedOrderIds: list[str] = Field(
        default=[], description="Echo of the requested order IDs; not a confirmation of modification.",
    )


class ModifyMultipleOrdersResult(ToolResult):
    data: ModifyMultipleOrdersData | None = None
