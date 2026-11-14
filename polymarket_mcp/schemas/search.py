from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class Market(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    question: str | None = None
    slug: str | None = None
    endDate: str | None = None
    category: str | None = None
    startDate: str | None = None
    image: str | None = None
    description: str | None = None
    active: bool | None = None
    marketType: str | None = Field(default=None, description="Deprecated market type: moneyline, spreads or totals.")
    closed: bool | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    archived: bool | None = None
    orderPriceMinTickSize: float | None = Field(default=None, description="Minimum tick size for order price.")
    gameStartTime: str | None = None
    manualActivation: bool | None = None
    sportsMarketType: str | None = None
    line: float | None = None
    marketSides: list[dict] | None = None
    outcomes: str | None = Field(default=None, description="Outcomes JSON (deprecated).")
    outcomePrices: str | None = Field(default=None, description="Outcome prices JSON (deprecated).")
    ep3Status: str | None = None
    sportsMarketTypeV2: str | None = None
    hidden: bool | None = None
    tags: list[dict] | None = None
    title: str | None = None
    subtitle: str | None = None
    color: str | None = None
    darkColor: str | None = None
    subjectId: int | None = None
    subject: dict | None = None
    feeCoefficient: float | None = None
    spreadTotalSuffix: str | None = Field(default=None, description="Spread/total suffix for UI display (e.g. points, goals, runs).")
    sortOrder: int | None = None
    bestBidQuote: dict | None = None
    bestAskQuote: dict | None = None
    metadata: dict | None = Field(default=None, description="Opaque internal-use metadata; shape is not part of the public contract.")
    titleShort: str | None = None
    ep3SyncedAt: str | None = None
    minimumTradeQty: float | None = Field(default=None, description="Minimum order quantity in contracts (e.g. 0.01 = 1% of a contract, 1.0 = one whole contract).")
    volume: float | None = Field(default=None, description="Market volume (lifetime, in shares).")
    volume24hr: float | None = Field(default=None, description="24-hour market volume (in shares).")
    volume1wk: float | None = Field(default=None, description="One week market volume (in shares).")
    volume1mo: float | None = Field(default=None, description="One month market volume (in shares).")
    volume1yr: float | None = Field(default=None, description="One year market volume (in shares).")
    rulesDisclaimer: str | None = None
    rulesDisclaimerPopup: bool | None = Field(default=None, description="When true, surface rulesDisclaimer as a popup the user acknowledges before buying, rather than inline.")
    comboEnabled: bool | None = None


class Event(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    resolutionSource: str | None = None
    startDate: str | None = None
    creationDate: str | None = None
    endDate: str | None = None
    image: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    liquidity: float | None = None
    volume: float | None = None
    openInterest: float | None = None
    category: str | None = None
    subcategory: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    volume24hr: float | None = None
    volume1wk: float | None = None
    volume1mo: float | None = None
    volume1yr: float | None = None
    closedTime: str | None = None
    eventDate: str | None = None
    startTime: str | None = None
    seriesSlug: str | None = None
    score: str | None = None
    elapsed: str | None = None
    period: str | None = None
    live: bool | None = None
    ended: bool | None = None
    finishedTimestamp: str | None = None
    featuredOrder: int | None = None
    markets: list[Market] | None = None
    gameId: int | None = Field(default=None, description="Game ID from the sports data provider.")
    rescheduledFromGameId: int | None = Field(default=None, description="Rescheduled game ID from the sports data provider.")
    sportradarGameId: str | None = None
    eventState: dict | None = None
    hidden: bool | None = None
    tags: list[dict] | None = None
    teams: list[dict] | None = None
    metadata: dict | None = None
    sortType: str | None = Field(default=None, description="Sort type for ordering markets within the event.")
    marketGroups: list[dict] | None = Field(default=None, description="Flat list of market groups forming a hierarchy via parent ID.")
    primaryTag: dict | None = None
    secondaryTag: dict | None = None
    primaryTagSlug: str | None = Field(default=None, description="Raw upstream replacement primary tag slug (admin-only; omitted on public reads).")
    secondaryTagSlug: str | None = Field(default=None, description="Raw upstream replacement secondary tag slug (admin-only; omitted on public reads).")
    livestreamUrl: str | None = None
    featureAvailability: dict | None = None
    comboEnabled: bool | None = Field(default=None, description="Whether this event has at least one combo-enabled market.")


class SearchEventsAndMarketsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    events: list[Event] = []


class SearchEventsAndMarketsResult(ToolResult):
    data: SearchEventsAndMarketsData | None = None

