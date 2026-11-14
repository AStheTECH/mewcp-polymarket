"""Events group: list_events, get_event_by_slug, get_event_by_id."""

import logging
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.events import (
    GetEventByIdData,
    GetEventByIdResult,
    GetEventBySlugData,
    GetEventBySlugResult,
    ListEventsData,
    ListEventsResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.events")


def register_events_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_events",
        description=(
            "Lists Polymarket events matching optional filters (status, tags, series, categories, "
            "liquidity/volume ranges, dates, sports game or team) and returns each event record with "
            "its markets, tags, teams and volume stats. Page through results with `limit` and `offset`; "
            "hidden events are excluded unless `includeHidden` is true."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_events(
        limit: int | None = Field(default=None, description="Maximum number of events to return. Omit for the API default."),
        offset: int | None = Field(default=None, description="Number of events to skip, for pagination. Omit to start at the first event."),
        orderBy: list[str] | None = Field(default=None, description="Event fields to order results by. Omit for the API default ordering."),
        orderDirection: str | None = Field(default=None, description="Order direction: 'asc' or 'desc'. Omit for the API default."),
        event_ids: list[int] | None = Field(default=None, description="Only return events with these numeric event IDs. Omit for no ID filter."),
        slug: list[str] | None = Field(default=None, description="Only return events with these slugs. Omit for no slug filter."),
        archived: bool | None = Field(default=None, description="Filter by archived status. Omit for no archived filter."),
        active: bool | None = Field(default=None, description="Filter by active status. Omit for no active filter."),
        closed: bool | None = Field(default=None, description="Filter by closed status. Omit for no closed filter."),
        liquidityMin: float | None = Field(default=None, description="Minimum event liquidity. Omit for no lower bound."),
        liquidityMax: float | None = Field(default=None, description="Maximum event liquidity. Omit for no upper bound."),
        volumeMin: float | None = Field(default=None, description="Minimum event volume. Omit for no lower bound."),
        volumeMax: float | None = Field(default=None, description="Maximum event volume. Omit for no upper bound."),
        startDateMin: str | None = Field(default=None, description="Minimum event start date. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        startDateMax: str | None = Field(default=None, description="Maximum event start date. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        endDateMin: str | None = Field(default=None, description="Minimum event end date. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        endDateMax: str | None = Field(default=None, description="Maximum event end date. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        relatedTags: bool | None = Field(default=None, description="Include related tags. Omit for the API default."),
        tagSlug: str | None = Field(default=None, description="Only return events with this single tag slug. Omit for no tag-slug filter."),
        userId: str | None = Field(default=None, description="Filter by user ID. Omit for no user filter."),
        featured: bool | None = Field(default=None, description="Filter by featured status. Omit for no featured filter."),
        seriesId: list[int] | None = Field(default=None, description="Only return events in these series IDs. Omit for no series filter."),
        eventDate: str | None = Field(default=None, description="Filter by event date. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no event-date filter."),
        startTimeMin: str | None = Field(default=None, description="Minimum event start time. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        startTimeMax: str | None = Field(default=None, description="Maximum event start time. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        excludeTagId: list[int] | None = Field(default=None, description="Exclude events carrying any of these tag IDs. Omit to exclude none."),
        featuredOrder: bool | None = Field(default=None, description="Order results by featured position. Omit for the API default ordering."),
        includeTemplate: bool | None = Field(default=None, description="Include template events. Omit for the API default."),
        recurrence: str | None = Field(default=None, description="Filter by recurrence type. Omit for no recurrence filter."),
        gameId: int | None = Field(default=None, description="Filter by sports data provider game ID. Omit for no game filter."),
        rescheduledFromGameId: int | None = Field(default=None, description="Filter by the game ID an event was rescheduled from. Omit for no filter."),
        period: str | None = Field(default=None, description="Filter by event period. Omit for no period filter."),
        finishedTimestampMin: str | None = Field(default=None, description="Minimum finished timestamp. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no lower bound."),
        finishedTimestampMax: str | None = Field(default=None, description="Maximum finished timestamp. ISO 8601 UTC datetime (e.g. '2026-11-01T00:00:00Z'); date-only or Unix values have no effect and raise no error. Omit for no upper bound."),
        ended: bool | None = Field(default=None, description="Filter by ended status. Omit for no ended filter."),
        sportradarGameId: str | None = Field(default=None, description="Filter by Sportradar game ID. Omit for no Sportradar filter."),
        excludeSeriesId: list[int] | None = Field(default=None, description="Exclude events in any of these series IDs. Omit to exclude none."),
        categories: list[str] | None = Field(default=None, description="Only return events in these categories (e.g. 'sports', 'crypto'). Omit for all categories."),
        marketTypes: list[str] | None = Field(default=None, description="Filter by market types. Omit for all market types."),
        live: bool | None = Field(default=None, description="Filter by live status. Omit for no live filter."),
        excludeEventId: list[int] | None = Field(default=None, description="Exclude these event IDs. Omit to exclude none."),
        includeHidden: bool | None = Field(default=None, description="Include hidden events. Omit to exclude hidden events (API default false)."),
        tagIds: list[int] | None = Field(default=None, description="Only return events carrying any of these tag IDs (OR). Omit for no tag-ID filter."),
        sportsMarketTypes: list[str] | None = Field(default=None, description="Filter by fine-grained sports market type (e.g. 'moneyline', 'drawable_outcome', 'soccer_game_to_advance'). Omit for all."),
        includeComboMarketCounts: bool | None = Field(default=None, description="Include derived event-level combo market counts. Omit for the API default."),
        teamId: int | None = Field(default=None, description="Only return events this team participates in. Omit for no team filter."),
        tagSlugsAll: list[str] | None = Field(default=None, description="Events must carry every one of these tag slugs (AND). Contrast `tagSlug` (single) and `tagIds` (OR). Omit for no filter."),
        includePopularPlayerProps: bool | None = Field(default=None, description="Include the synthetic Popular section in Player Props market groups. Omit for the API default."),
    ) -> ListEventsResult:
        tlog = ToolLogger(logger, "list_events")
        params = {
            "limit": limit,
            "offset": offset,
            "orderBy": orderBy,
            "orderDirection": orderDirection,
            "id": event_ids,
            "slug": slug,
            "archived": archived,
            "active": active,
            "closed": closed,
            "liquidityMin": liquidityMin,
            "liquidityMax": liquidityMax,
            "volumeMin": volumeMin,
            "volumeMax": volumeMax,
            "startDateMin": startDateMin,
            "startDateMax": startDateMax,
            "endDateMin": endDateMin,
            "endDateMax": endDateMax,
            "relatedTags": relatedTags,
            "tagSlug": tagSlug,
            "userId": userId,
            "featured": featured,
            "seriesId": seriesId,
            "eventDate": eventDate,
            "startTimeMin": startTimeMin,
            "startTimeMax": startTimeMax,
            "excludeTagId": excludeTagId,
            "featuredOrder": featuredOrder,
            "includeTemplate": includeTemplate,
            "recurrence": recurrence,
            "gameId": gameId,
            "rescheduledFromGameId": rescheduledFromGameId,
            "period": period,
            "finishedTimestampMin": finishedTimestampMin,
            "finishedTimestampMax": finishedTimestampMax,
            "ended": ended,
            "sportradarGameId": sportradarGameId,
            "excludeSeriesId": excludeSeriesId,
            "categories": categories,
            "marketTypes": marketTypes,
            "live": live,
            "excludeEventId": excludeEventId,
            "includeHidden": includeHidden,
            "tagIds": tagIds,
            "sportsMarketTypes": sportsMarketTypes,
            "includeComboMarketCounts": includeComboMarketCounts,
            "teamId": teamId,
            "tagSlugsAll": tagSlugsAll,
            "includePopularPlayerProps": includePopularPlayerProps,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/events", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListEventsResult(success=True, statusCode=status, data=ListEventsData(**data))
            return _upstream_err(ListEventsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListEventsResult, tlog, exc)

    @mcp.tool(
        name="get_event_by_slug",
        description=(
            "Retrieves a single Polymarket event by its URL slug and returns the full event record, "
            "including its markets, tags, teams, live state and volume stats. Set `groups` to true to "
            "also get the structured market group hierarchy (`marketGroups`); use get_event_by_id when "
            "you have the numeric event ID instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_event_by_slug(
        slug: str = Field(description="Event slug as used in the event URL (e.g. 'super-bowl-2025')."),
        groups: bool | None = Field(default=None, description="Include structured market groups (`marketGroups`) in the response. Omit to leave them out."),
        comboEnabledOnly: bool | None = Field(default=None, description="When true, return only combo-enabled markets for the event. Omit to return all markets."),
        includePopularPlayerProps: bool | None = Field(default=None, description="Include the synthetic Popular section in Player Props market groups. Omit for the API default."),
    ) -> GetEventBySlugResult:
        tlog = ToolLogger(logger, "get_event_by_slug")
        if not slug.strip():
            return _err(GetEventBySlugResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        params = {
            "groups": groups,
            "comboEnabledOnly": comboEnabledOnly,
            "includePopularPlayerProps": includePopularPlayerProps,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/events/slug/{quote(slug, safe='')}", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetEventBySlugResult(success=True, statusCode=status, data=GetEventBySlugData(**data))
            return _upstream_err(GetEventBySlugResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetEventBySlugResult, tlog, exc)

    @mcp.tool(
        name="get_event_by_id",
        description=(
            "Retrieves a single Polymarket event by its numeric event ID and returns the full event record, "
            "including its markets, tags, teams, live state and volume stats. Set `groups` to true to also "
            "get the structured market group hierarchy (`marketGroups`); use get_event_by_slug when you "
            "have the event slug instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_event_by_id(
        event_id: int = Field(description="Numeric event ID (e.g. 12345)."),
        groups: bool | None = Field(default=None, description="Include structured market groups (`marketGroups`) in the response. Omit to leave them out."),
        comboEnabledOnly: bool | None = Field(default=None, description="When true, return only combo-enabled markets for the event. Omit to return all markets."),
        includePopularPlayerProps: bool | None = Field(default=None, description="Include the synthetic Popular section in Player Props market groups. Omit for the API default."),
    ) -> GetEventByIdResult:
        tlog = ToolLogger(logger, "get_event_by_id")
        params = {
            "groups": groups,
            "comboEnabledOnly": comboEnabledOnly,
            "includePopularPlayerProps": includePopularPlayerProps,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/events/{event_id}", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetEventByIdResult(success=True, statusCode=status, data=GetEventByIdData(**data))
            return _upstream_err(GetEventByIdResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetEventByIdResult, tlog, exc)
