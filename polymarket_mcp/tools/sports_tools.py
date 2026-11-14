"""Sports group: list_sports, get_sport_by_slug, list_sport_events, list_leagues, get_league_by_slug, list_league_events"""

import logging
from typing import Literal
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.sports import (
    GetLeagueBySlugData,
    GetLeagueBySlugResult,
    GetSportBySlugData,
    GetSportBySlugResult,
    ListLeagueEventsData,
    ListLeagueEventsResult,
    ListLeaguesData,
    ListLeaguesResult,
    ListSportEventsData,
    ListSportEventsResult,
    ListSportsData,
    ListSportsResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.sports")

_READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)


def _page_error(limit: int | None, offset: int | None) -> str | None:
    if limit is not None and limit < 1:
        return "limit must be at least 1"
    if offset is not None and offset < 0:
        return "offset must be 0 or greater"
    return None


def register_sports_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_sports",
        description=(
            "Lists all sports. Returns each sport's ID, slug, name, image and tag ID, "
            "with its leagues (ID, slug, name, abbreviation, active series ID) nested under it."
        ),
        annotations=_READ_ONLY,
    )
    def list_sports() -> ListSportsResult:
        tlog = ToolLogger(logger, "list_sports")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v2/sports", timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListSportsResult(success=True, statusCode=status, data=ListSportsData(**data))
            return _upstream_err(ListSportsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListSportsResult, tlog, exc)

    @mcp.tool(
        name="get_sport_by_slug",
        description=(
            "Gets a single sport by its slug. Returns the sport's ID, name, image and tag ID "
            "with all of its leagues attached."
        ),
        annotations=_READ_ONLY,
    )
    def get_sport_by_slug(
        slug: str = Field(description="Sport slug, as returned by list_sports (e.g. 'football')."),
    ) -> GetSportBySlugResult:
        tlog = ToolLogger(logger, "get_sport_by_slug")
        if not slug.strip():
            return _err(GetSportBySlugResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/sports/{quote(slug, safe='')}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetSportBySlugResult(success=True, statusCode=status, data=GetSportBySlugData(**data))
            return _upstream_err(GetSportBySlugResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetSportBySlugResult, tlog, exc)

    @mcp.tool(
        name="list_sport_events",
        description=(
            "Lists events for a sport by its slug, in either the games ('sport') or 'futures' tab "
            "and the 'general' or 'trending' section. Returns the events (with markets, teams, "
            "live score and state) plus the sport record; page with limit/offset."
        ),
        annotations=_READ_ONLY,
    )
    def list_sport_events(
        slug: str = Field(description="Sport slug, as returned by list_sports (e.g. 'football', 'basketball')."),
        limit: int | None = Field(default=None, description="Maximum number of events to return. Omit for the API default."),
        offset: int | None = Field(default=None, description="Number of events to skip for pagination. Omit to start from the first event."),
        excludeEventId: list[int] | None = Field(default=None, description="Event IDs to leave out of the results. Omit to exclude none."),
        event_type: Literal["sport", "futures"] = Field(default="sport", description="Event type: 'sport' for games or 'futures' for futures markets."),
        section: Literal["general", "trending"] = Field(default="general", description="Section to list: 'general' or 'trending'."),
    ) -> ListSportEventsResult:
        tlog = ToolLogger(logger, "list_sport_events")
        if not slug.strip():
            return _err(ListSportEventsResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        page_err = _page_error(limit, offset)
        if page_err:
            return _err(ListSportEventsResult, tlog, "VALIDATION_ERROR", page_err, 400)
        params = {
            "limit": limit,
            "offset": offset,
            "excludeEventId": excludeEventId,
            "type": event_type,
            "section": section,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/sports/{quote(slug, safe='')}/events", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListSportEventsResult(success=True, statusCode=status, data=ListSportEventsData(**data))
            return _upstream_err(ListSportEventsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListSportEventsResult, tlog, exc)

    @mcp.tool(
        name="list_leagues",
        description=(
            "Lists leagues across all sports, at most 50 per page. Returns each league's ID, slug, "
            "name, abbreviation, parent sport ID and active series ID; page with limit/offset."
        ),
        annotations=_READ_ONLY,
    )
    def list_leagues(
        limit: int = Field(default=50, description="Maximum number of leagues to return (1-50)."),
        offset: int = Field(default=0, description="Number of leagues to skip for pagination."),
    ) -> ListLeaguesResult:
        tlog = ToolLogger(logger, "list_leagues")
        if limit < 1 or limit > 50:
            return _err(ListLeaguesResult, tlog, "VALIDATION_ERROR", "limit must be 1-50", 400)
        if offset < 0:
            return _err(ListLeaguesResult, tlog, "VALIDATION_ERROR", "offset must be 0 or greater", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v2/leagues", params={"limit": limit, "offset": offset},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListLeaguesResult(success=True, statusCode=status, data=ListLeaguesData(**data))
            return _upstream_err(ListLeaguesResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListLeaguesResult, tlog, exc)

    @mcp.tool(
        name="get_league_by_slug",
        description=(
            "Gets a single league by its slug. Returns the league's ID, name, abbreviation, "
            "parent sport ID, tag ID, active series ID and operational status."
        ),
        annotations=_READ_ONLY,
    )
    def get_league_by_slug(
        slug: str = Field(description="League slug, as returned by list_leagues or list_sports (e.g. 'nfl')."),
    ) -> GetLeagueBySlugResult:
        tlog = ToolLogger(logger, "get_league_by_slug")
        if not slug.strip():
            return _err(GetLeagueBySlugResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/leagues/{quote(slug, safe='')}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetLeagueBySlugResult(success=True, statusCode=status, data=GetLeagueBySlugData(**data))
            return _upstream_err(GetLeagueBySlugResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetLeagueBySlugResult, tlog, exc)

    @mcp.tool(
        name="list_league_events",
        description=(
            "Lists events for a league by its slug, taken from the league's active series, in either "
            "the games ('sport') or 'futures' tab and the 'general' or 'trending' section. Returns the "
            "events (with markets, teams, live score and state) plus the league record; page with limit/offset."
        ),
        annotations=_READ_ONLY,
    )
    def list_league_events(
        slug: str = Field(description="League slug, as returned by list_leagues (e.g. 'nfl', 'nba')."),
        limit: int | None = Field(default=None, description="Maximum number of events to return. Omit for the API default."),
        offset: int | None = Field(default=None, description="Number of events to skip for pagination. Omit to start from the first event."),
        excludeEventId: list[int] | None = Field(default=None, description="Event IDs to leave out of the results. Omit to exclude none."),
        event_type: Literal["sport", "futures"] = Field(default="sport", description="Event type: 'sport' for games or 'futures' for futures markets."),
        section: Literal["general", "trending"] = Field(default="general", description="Section to list: 'general' or 'trending'."),
    ) -> ListLeagueEventsResult:
        tlog = ToolLogger(logger, "list_league_events")
        if not slug.strip():
            return _err(ListLeagueEventsResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        page_err = _page_error(limit, offset)
        if page_err:
            return _err(ListLeagueEventsResult, tlog, "VALIDATION_ERROR", page_err, 400)
        params = {
            "limit": limit,
            "offset": offset,
            "excludeEventId": excludeEventId,
            "type": event_type,
            "section": section,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/leagues/{quote(slug, safe='')}/events", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListLeagueEventsResult(success=True, statusCode=status, data=ListLeagueEventsData(**data))
            return _upstream_err(ListLeagueEventsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListLeagueEventsResult, tlog, exc)
