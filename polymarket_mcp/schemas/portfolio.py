from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class Amount(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: str | None = Field(default=None, description="Amount as a decimal string (e.g. '123.45').")
    currency: str | None = None


class MarketMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str | None = None
    icon: str | None = Field(default=None, description="Market image URL.")
    title: str | None = None
    outcome: str | None = None
    eventSlug: str | None = None


class UserPosition(BaseModel):
    model_config = ConfigDict(extra="allow")

    netPosition: str | None = Field(default=None, description="Deprecated whole-number net quantity; use netPositionDecimal.")
    qtyBought: str | None = Field(default=None, description="Deprecated whole-number quantity bought; use qtyBoughtDecimal.")
    qtySold: str | None = Field(default=None, description="Deprecated whole-number quantity sold; use qtySoldDecimal.")
    cost: Amount | None = Field(default=None, description="Total cost basis.")
    realized: Amount | None = Field(default=None, description="Realized profit/loss.")
    bodPosition: str | None = Field(default=None, description="Deprecated whole-number beginning-of-day position; use bodPositionDecimal.")
    expired: bool | None = None
    updateTime: str | None = None
    marketMetadata: MarketMetadata | None = None
    cashValue: Amount | None = Field(default=None, description="Unrealized PnL for the position.")
    qtyAvailable: str | None = Field(default=None, description="Deprecated whole-number quantity available to trade; use qtyAvailableDecimal.")
    netPositionDecimal: str | None = Field(default=None, description="Net position quantity as a decimal string.")
    qtyBoughtDecimal: str | None = Field(default=None, description="Total quantity bought as a decimal string.")
    qtySoldDecimal: str | None = Field(default=None, description="Total quantity sold as a decimal string.")
    bodPositionDecimal: str | None = Field(default=None, description="Beginning-of-day position as a decimal string.")
    qtyAvailableDecimal: str | None = Field(default=None, description="Quantity available to trade as a decimal string.")


class ListPositionsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    positions: dict[str, UserPosition] = Field(default_factory=dict, description="Map of market slug to position.")
    nextCursor: str | None = Field(default=None, description="Pass as `cursor` to fetch the next page.")
    eof: bool | None = Field(default=None, description="True if this is the last page.")
    availablePositions: list[str] | None = Field(default=None, description="Deprecated: available position quantities factoring in open orders.")


class ListPositionsResult(ToolResult):
    data: ListPositionsData | None = None


class Trade(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    marketSlug: str | None = None
    state: str | None = Field(default=None, description=(
        "TRADE_STATE_NEW, TRADE_STATE_CLEARED, TRADE_STATE_BUSTED, TRADE_STATE_INFLIGHT, "
        "TRADE_STATE_PENDING_RISK, TRADE_STATE_PENDING_CLEARED or TRADE_STATE_REJECTED."
    ))
    createTime: str | None = None
    updateTime: str | None = None
    price: Amount | None = None
    qty: str | None = Field(default=None, description="Deprecated whole-number trade quantity; use qtyDecimal.")
    isAggressor: bool | None = Field(default=None, description="True if the user's order was the taker.")
    costBasis: Amount | None = None
    realizedPnl: Amount | None = None
    qtyDecimal: str | None = Field(default=None, description="Trade quantity as a decimal string.")


class PositionResolution(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketSlug: str | None = None
    beforePosition: UserPosition | None = None
    afterPosition: UserPosition | None = None
    updateTime: str | None = None
    tradeId: str | None = None
    side: str | None = Field(default=None, description=(
        "POSITION_RESOLUTION_SIDE_LONG, POSITION_RESOLUTION_SIDE_SHORT or POSITION_RESOLUTION_SIDE_NEUTRAL."
    ))


class AccountBalanceChange(BaseModel):
    model_config = ConfigDict(extra="allow")

    transactionId: str | None = None
    status: str | None = Field(default=None, description=(
        "ACCOUNT_BALANCE_CHANGE_STATUS_PENDING, ACCOUNT_BALANCE_CHANGE_STATUS_COMPLETED, "
        "ACCOUNT_BALANCE_CHANGE_STATUS_PARTIALLY_REFUNDED or ACCOUNT_BALANCE_CHANGE_STATUS_REJECTED."
    ))
    amount: Amount | None = None
    updateTime: str | None = None
    createTime: str | None = None


class Activity(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = Field(default=None, description="Activity type (ACTIVITY_TYPE_*); selects which of trade, positionResolution or accountBalanceChange is set.")
    trade: Trade | None = None
    positionResolution: PositionResolution | None = None
    accountBalanceChange: AccountBalanceChange | None = None


class ListActivitiesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    activities: list[Activity] = Field(default_factory=list)
    nextCursor: str | None = Field(default=None, description="Pass as `cursor` to fetch the next page.")
    eof: bool | None = Field(default=None, description="True if this is the last page.")


class ListActivitiesResult(ToolResult):
    data: ListActivitiesData | None = None
