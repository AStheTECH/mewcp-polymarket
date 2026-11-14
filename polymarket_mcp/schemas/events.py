"""Schemas for the events group: list_events, get_event_by_slug, get_event_by_id."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


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
    imageDisplayType: str | None = Field(
        default=None,
        description=(
            "One of IMAGE_DISPLAY_TYPE_HEADSHOT, IMAGE_DISPLAY_TYPE_LOGO, "
            "IMAGE_DISPLAY_TYPE_FLAG, IMAGE_DISPLAY_TYPE_ARTWORK."
        ),
    )
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
    markets: list[dict[str, Any]] | None = None
    gameId: int | None = Field(default=None, description="Game ID from the sports data provider.")
    rescheduledFromGameId: int | None = Field(
        default=None, description="Sports data provider game ID this event was rescheduled from."
    )
    sportradarGameId: str | None = None
    eventState: dict[str, Any] | None = None
    hidden: bool | None = None
    tags: list[dict[str, Any]] | None = None
    teams: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    sortType: str | None = Field(default=None, description="Sort type for ordering markets within the event.")
    marketGroups: list[dict[str, Any]] | None = Field(
        default=None,
        description="Flat list of market groups forming a hierarchy via parent ID; present only when groups=true.",
    )
    primaryTag: dict[str, Any] | None = None
    secondaryTag: dict[str, Any] | None = None
    primaryTagSlug: str | None = Field(
        default=None, description="Raw primary tag slug override; admin-only, omitted on public reads."
    )
    secondaryTagSlug: str | None = Field(
        default=None, description="Raw secondary tag slug override; admin-only, omitted on public reads."
    )
    livestreamUrl: str | None = None
    streamProvider: str | None = Field(
        default=None,
        description="Stream provider identifier (e.g. 'beter') when the event has a resolvable stream; empty means none.",
    )
    streamRequiresAuth: bool | None = Field(
        default=None,
        description="When true, the event stream only resolves for authenticated requests. Always false when streamProvider is empty.",
    )
    featureAvailability: dict[str, Any] | None = None
    combos: dict[str, Any] | None = None
    marketCounts: dict[str, Any] | None = None


class ListEventsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    events: list[Event] = Field(default_factory=list)


class ListEventsResult(ToolResult):
    data: ListEventsData | None = None


class GetEventBySlugData(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: Event | None = None


class GetEventBySlugResult(ToolResult):
    data: GetEventBySlugData | None = None


class GetEventByIdData(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: Event | None = None


class GetEventByIdResult(ToolResult):
    data: GetEventByIdData | None = None
