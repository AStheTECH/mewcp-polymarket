"""Sports group schemas: sports, leagues and their events."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class League(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    image: str | None = None
    isOperational: bool | None = None
    sportId: int | None = None
    tagId: int | None = None
    resolution: str | None = None
    ordering: str | None = None
    activeSeriesId: int | None = None
    createdAt: str | None = None
    abbreviation: str | None = None


class Sport(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    slug: str | None = None
    name: str | None = None
    image: str | None = None
    tagId: int | None = None
    createdAt: str | None = None
    defaultJerseyImage: str | None = None


class SportWithLeagues(Sport):
    leagues: list[League] | None = None


class SportsEvent(BaseModel):
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
    markets: list[dict[str, Any]] | None = None
    gameId: int | None = Field(default=None, description="Game ID from the sports data provider")
    rescheduledFromGameId: int | None = Field(
        default=None, description="Sports-provider game ID this event was rescheduled from"
    )
    sportradarGameId: str | None = None
    eventState: dict[str, Any] | None = None
    hidden: bool | None = None
    tags: list[dict[str, Any]] | None = None
    teams: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    sortType: str | None = Field(default=None, description="Sort type for ordering markets within the event")
    marketGroups: list[dict[str, Any]] | None = Field(
        default=None, description="Flat list of market groups forming a hierarchy via parent_id"
    )
    primaryTag: dict[str, Any] | None = None
    secondaryTag: dict[str, Any] | None = None
    primaryTagSlug: str | None = None
    secondaryTagSlug: str | None = None
    livestreamUrl: str | None = None
    featureAvailability: dict[str, Any] | None = Field(
        default=None, description="Data surfaces available for this event (lineups, timeline)"
    )


# list_sports

class ListSportsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    sports: list[SportWithLeagues] | None = None


class ListSportsResult(ToolResult):
    data: ListSportsData | None = None


# get_sport_by_slug

class GetSportBySlugData(BaseModel):
    model_config = ConfigDict(extra="allow")

    sport: SportWithLeagues | None = None


class GetSportBySlugResult(ToolResult):
    data: GetSportBySlugData | None = None


# list_sport_events

class ListSportEventsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = Field(default=None, description="Event type: sport or futures")
    typeTitle: str | None = Field(default=None, description="Subtab title: Games or Futures")
    section: str | None = Field(default=None, description="Section: general or trending")
    sectionTitle: str | None = Field(default=None, description="Section title: Sport or Trending")
    events: list[SportsEvent] | None = None
    sport: Sport | None = None


class ListSportEventsResult(ToolResult):
    data: ListSportEventsData | None = None


# list_leagues

class ListLeaguesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    leagues: list[League] | None = None


class ListLeaguesResult(ToolResult):
    data: ListLeaguesData | None = None


# get_league_by_slug

class GetLeagueBySlugData(BaseModel):
    model_config = ConfigDict(extra="allow")

    league: League | None = None


class GetLeagueBySlugResult(ToolResult):
    data: GetLeagueBySlugData | None = None


# list_league_events

class ListLeagueEventsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = Field(default=None, description="Event type: sport or futures")
    typeTitle: str | None = Field(default=None, description="Subtab title: Games or Futures")
    section: str | None = Field(default=None, description="Section: general or trending")
    sectionTitle: str | None = Field(default=None, description="Section title: Sport or Trending")
    events: list[SportsEvent] | None = None
    league: League | None = None


class ListLeagueEventsResult(ToolResult):
    data: ListLeagueEventsData | None = None
