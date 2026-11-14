"""Schemas for the markets group."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult

_STATE_DESC = (
    "Book state: MARKET_STATE_OPEN, MARKET_STATE_PREOPEN, MARKET_STATE_SUSPENDED, "
    "MARKET_STATE_EXPIRED, MARKET_STATE_TERMINATED, MARKET_STATE_HALTED or "
    "MARKET_STATE_MATCH_AND_CLOSE_AUCTION."
)


class Amount(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: str | None = Field(default=None, description="The amount as a decimal string.")
    currency: str | None = None


class MarketSide(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    marketSideType: str | None = Field(
        default=None, description="MARKET_SIDE_TYPE_ERC1155 or MARKET_SIDE_TYPE_INSTRUMENT.")
    identifier: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    description: str | None = None
    price: str | None = None
    marketId: int | None = None
    long: bool | None = Field(
        default=None, description="Whether this side is the long (true) or short (false) side of the market.")
    teamId: int | None = None
    team: dict[str, Any] | None = None
    quote: Amount | None = None
    tradable: bool | None = None


class AssetPriceTerms(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketType: str | None = Field(
        default=None,
        description="How the market settles: ASSET_PRICE_MARKET_TYPE_UP_DOWN, _ABOVE_BELOW, _RANGE, "
                    "_ONE_TOUCH, _DATE, _FIRST_TO_HIT, or _UNSPECIFIED for a type newer than the schema.")
    asset: dict[str, Any] | None = Field(
        default=None, description="Priced asset: `assetClass` (ASSET_CLASS_CRYPTO or ASSET_CLASS_COMMODITY) and `symbol` (e.g. btc, gold).")
    indexSymbol: str | None = Field(
        default=None, description="Reference index the market settles on, e.g. BRTI. Empty on gold and silver markets.")
    horizon: str | None = None
    windowStart: str | None = None
    windowEnd: str | None = Field(
        default=None, description="Scheduled settlement instant; use this rather than the market endDate.")
    priceToBeat: Amount | None = None
    strike: Amount | None = None
    rangeLower: Amount | None = None
    rangeUpper: Amount | None = None
    rangeKind: str | None = Field(
        default=None,
        description="Open side of a RANGE market: ASSET_PRICE_RANGE_KIND_INTERIOR, _BELOW, _ABOVE, or _UNSPECIFIED.")
    direction: str | None = Field(
        default=None, description="ONE_TOUCH direction: ASSET_PRICE_DIRECTION_UP, _DOWN, or _UNSPECIFIED.")
    settlementPrice: Amount | None = None
    priceDecimals: int | None = Field(
        default=None, description="Decimal places every price of this market carries.")
    assetName: str | None = None
    priceUnit: str | None = None
    nextWindowStart: str | None = None


class Subject(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    displayName: str | None = None
    description: str | None = None
    subjectType: str | None = Field(
        default=None, description="Subject type (nominee, player, team, candidate, golf_player).")
    image: str | None = None
    color: str | None = None
    darkColor: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    slug: str | None = None


class MarketTag(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    label: str | None = None
    slug: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    image: str | None = None
    tradable: bool | None = None
    league: dict[str, Any] | None = None
    sport: dict[str, Any] | None = None
    parentId: int | None = None
    subtags: list[dict[str, Any]] | None = None
    hub: dict[str, Any] | None = None


class Market(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    question: str | None = None
    slug: str | None = Field(
        default=None, description="Market slug; the identifier used by the book, BBO, settlement, price-history and order tools.")
    endDate: str | None = None
    category: str | None = None
    startDate: str | None = None
    image: str | None = None
    imageDisplayType: str | None = Field(
        default=None,
        description="IMAGE_DISPLAY_TYPE_HEADSHOT, IMAGE_DISPLAY_TYPE_LOGO, IMAGE_DISPLAY_TYPE_FLAG or IMAGE_DISPLAY_TYPE_ARTWORK.")
    description: str | None = None
    active: bool | None = None
    marketType: str | None = Field(
        default=None, description="Deprecated market type: moneyline, spreads or totals.")
    closed: bool | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    archived: bool | None = None
    orderPriceMinTickSize: float | None = None
    gameStartTime: str | None = None
    manualActivation: bool | None = None
    sportsMarketType: str | None = None
    line: float | None = None
    marketSides: list[MarketSide] | None = None
    outcomes: str | None = Field(default=None, description="Outcomes as a JSON-encoded string.")
    outcomePrices: str | None = Field(default=None, description="Outcome prices as a JSON-encoded string (deprecated).")
    ep3Status: str | None = Field(default=None, description="Deprecated raw upstream state; use `status`.")
    status: str | None = Field(
        default=None,
        description="Normalized lifecycle: MARKET_STATUS_OPEN, _CLOSED, _RESOLVING (past expiry, payouts pending), "
                    "_RESOLVED (final settlement published), _HALTED, or _UNSPECIFIED (also used for unrecognized values).")
    assetPriceTerms: AssetPriceTerms | None = Field(
        default=None, description="Terms of an automated crypto/commodity price market; null on every other market.")
    sportsMarketTypeV2: str | None = None
    hidden: bool | None = None
    tags: list[MarketTag] | None = None
    title: str | None = None
    subtitle: str | None = None
    color: str | None = None
    darkColor: str | None = None
    subjectId: int | None = None
    subject: Subject | None = None
    feeCoefficient: float | None = None
    spreadTotalSuffix: str | None = None
    sortOrder: int | None = None
    bestBidQuote: Amount | None = None
    bestAskQuote: Amount | None = None
    metadata: dict[str, Any] | None = Field(
        default=None, description="Opaque internal-use metadata; shape is not part of the public contract.")
    titleShort: str | None = None
    ep3SyncedAt: str | None = None
    minimumTradeQty: float | None = Field(
        default=None, description="Minimum order quantity in contracts (e.g. 0.01 = 1% of a contract).")
    volume: float | None = Field(default=None, description="Lifetime volume in shares.")
    volume24hr: float | None = Field(default=None, description="24-hour volume in shares.")
    volume1wk: float | None = Field(default=None, description="One-week volume in shares.")
    volume1mo: float | None = Field(default=None, description="One-month volume in shares.")
    volume1yr: float | None = Field(default=None, description="One-year volume in shares.")
    rulesDisclaimer: str | None = None
    rulesDisclaimerPopup: bool | None = None
    comboEnabled: bool | None = None


class ListMarketsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    markets: list[Market] = Field(default_factory=list)


class ListMarketsResult(ToolResult):
    data: ListMarketsData | None = None


class GetMarketByIdData(BaseModel):
    model_config = ConfigDict(extra="allow")

    market: Market | None = None


class GetMarketByIdResult(ToolResult):
    data: GetMarketByIdData | None = None


class GetMarketBySlugData(BaseModel):
    model_config = ConfigDict(extra="allow")

    market: Market | None = None


class GetMarketBySlugResult(ToolResult):
    data: GetMarketBySlugData | None = None


class PriceSample(BaseModel):
    model_config = ConfigDict(extra="allow")

    longPx: Amount | None = None
    shortPx: Amount | None = None
    ts: str | None = None


class MarketDataLite(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketSlug: str | None = None
    currentPx: Amount | None = None
    lastTradePx: Amount | None = None
    settlementPx: Amount | None = None
    sharesTraded: str | None = None
    openInterest: str | None = None
    bestAsk: Amount | None = None
    bestBid: Amount | None = None
    askDepth: int | None = Field(default=None, description="Number of price levels on the offer side (not shares).")
    bidDepth: int | None = Field(default=None, description="Number of price levels on the bid side (not shares).")
    lastPriceSample: PriceSample | None = None
    longQuote: Amount | None = None
    shortQuote: Amount | None = None
    state: str | None = Field(default=None, description=_STATE_DESC)
    bidShares: str | None = Field(
        default=None, description="Total shares resting on the bid side, rounded down to two significant figures; \"0\" when empty.")
    askShares: str | None = Field(
        default=None, description="Total shares resting on the offer side, rounded down to two significant figures; \"0\" when empty.")


class GetMarketBboData(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketData: MarketDataLite | None = None


class GetMarketBboResult(ToolResult):
    data: GetMarketBboData | None = None


class BookEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    px: Amount | None = None
    qty: str | None = None


class MarketStats(BaseModel):
    model_config = ConfigDict(extra="allow")

    openPx: Amount | None = None
    closePx: Amount | None = None
    lowPx: Amount | None = None
    highPx: Amount | None = None
    lastTradePx: Amount | None = None
    indicativeOpenPx: Amount | None = None
    settlementPx: Amount | None = None
    sharesTraded: str | None = None
    notionalTraded: Amount | None = None
    lastTradeQty: str | None = None
    openInterest: str | None = None
    settlementPreliminaryFlag: bool | None = None
    openSetTime: str | None = None
    closeSetTime: str | None = None
    highSetTime: str | None = None
    lowSetTime: str | None = None
    lastTradeSetTime: str | None = None
    indicativeOpenSetTime: str | None = None
    settlementSetTime: str | None = None
    openInterestSetTime: str | None = None
    notionalSetTime: str | None = None
    settlementPriceCalculationMethod: str | None = Field(
        default=None,
        description="How the settlement price was calculated (SETTLEMENT_PRICE_CALCULATION_METHOD_*: VWAP tiers, "
                    "EVENT tiers, or OVERRIDE). EVENT_TIER_1 means the price was set by resolution and is final.")
    tradingReferencePx: Amount | None = None
    tradingReferenceSetTime: str | None = None
    currentPx: Amount | None = None
    lastPriceSample: PriceSample | None = None


class MarketBookData(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketSlug: str | None = None
    bids: list[BookEntry] | None = None
    offers: list[BookEntry] | None = None
    state: str | None = Field(default=None, description=_STATE_DESC)
    stats: MarketStats | None = None
    transactTime: str | None = None


class GetMarketBookData(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketData: MarketBookData | None = None


class GetMarketBookResult(ToolResult):
    data: GetMarketBookData | None = None


class GetMarketSettlementData(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str | None = None
    settlement: float | None = Field(default=None, description="Settlement price.")


class GetMarketSettlementResult(ToolResult):
    data: GetMarketSettlementData | None = None


class PriceHistoryPoint(BaseModel):
    model_config = ConfigDict(extra="allow")

    timestamp: int | None = Field(default=None, description="Observation time in Unix seconds.")
    longPrice: float | None = Field(
        default=None, description="Yes display price, normally derived from the best ask.")
    shortPrice: float | None = Field(
        default=None, description="No display price, normally derived from one minus the best bid.")


class GetPriceHistoryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    history: list[PriceHistoryPoint] = Field(default_factory=list)


class GetPriceHistoryResult(ToolResult):
    data: GetPriceHistoryData | None = None
