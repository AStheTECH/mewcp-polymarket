from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class TagLeague(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    sportId: int | None = None
    tagId: int | None = None
    image: str | None = None
    resolution: str | None = None
    ordering: str | None = None
    activeSeriesId: int | None = None
    isOperational: bool | None = None
    automaticResolution: bool | None = None
    createdAt: str | None = None
    slug: str | None = None
    abbreviation: str | None = None


class TagSport(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    tagId: int | None = None
    createdAt: str | None = None
    slug: str | None = None
    image: str | None = None


class Tag(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    label: str | None = None
    slug: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    image: str | None = None
    tradable: bool | None = None
    league: TagLeague | None = None
    sport: TagSport | None = None
    parentId: int | None = None
    subtags: list[dict[str, Any]] | None = Field(
        default=None, description="Child subtags (same shape as a tag, nested recursively)."
    )


class ListTagsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    tags: list[Tag] = []


class ListTagsResult(ToolResult):
    data: ListTagsData | None = None


class GetTagBySlugData(BaseModel):
    model_config = ConfigDict(extra="allow")

    tag: Tag | None = None


class GetTagBySlugResult(ToolResult):
    data: GetTagBySlugData | None = None


class GetTagByIdData(BaseModel):
    model_config = ConfigDict(extra="allow")

    tag: Tag | None = None


class GetTagByIdResult(ToolResult):
    data: GetTagByIdData | None = None


class TagEvent(BaseModel):
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
    liquidity: float | str | None = Field(default=None, description="Event liquidity (decimal).")
    volume: float | str | None = Field(default=None, description="Event volume (decimal).")
    openInterest: float | str | None = Field(default=None, description="Open interest (decimal).")
    category: str | None = None
    subcategory: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    volume24hr: float | str | None = None
    volume1wk: float | str | None = None
    volume1mo: float | str | None = None
    volume1yr: float | str | None = None
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
    markets: list[dict[str, Any]] | None = None
    gameId: int | None = Field(default=None, description="Game ID from the sports data provider.")
    rescheduledFromGameId: int | None = Field(
        default=None, description="Sports-provider game ID this event was rescheduled from."
    )
    sportradarGameId: str | None = None
    eventState: dict[str, Any] | None = None
    hidden: bool | None = None
    tags: list[Tag] | None = None
    teams: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    sortType: str | None = Field(default=None, description="Sort type for ordering markets within the event.")
    marketGroups: list[dict[str, Any]] | None = Field(
        default=None, description="Flat list of market groups forming a hierarchy via parentId."
    )
    primaryTag: Tag | None = None
    secondaryTag: Tag | None = None
    primaryTagSlug: str | None = Field(
        default=None, description="Admin-only replacement primary tag slug; omitted on public reads."
    )
    secondaryTagSlug: str | None = Field(
        default=None, description="Admin-only replacement secondary tag slug; omitted on public reads."
    )
    livestreamUrl: str | None = None
    featureAvailability: dict[str, Any] | None = None


class ListTagEventsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    events: list[TagEvent] = []


class ListTagEventsResult(ToolResult):
    data: ListTagEventsData | None = None
