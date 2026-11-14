"""Tags group: list_tags, get_tag_by_slug, get_tag_by_id, list_tag_events"""

import logging
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.tags import (
    GetTagByIdData,
    GetTagByIdResult,
    GetTagBySlugData,
    GetTagBySlugResult,
    ListTagEventsData,
    ListTagEventsResult,
    ListTagsData,
    ListTagsResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.tags")


def register_tags_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="list_tags",
        description=(
            "Lists tags in ranked order, optionally filtered by slug, tag IDs, parent tag or a "
            "case-insensitive label substring. Returns each tag's ID, label, slug, image, "
            "tradable flag, league and sport details, parent ID and subtags. "
            "If both parentSlug and parentId are given, parentSlug takes precedence over parentId."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_tags(
        limit: int | None = Field(default=None, description="Maximum number of tags to return. Omit for the server default."),
        offset: int | None = Field(default=None, description="Number of tags to skip for pagination. Omit to start from the first tag."),
        orderBy: list[str] | None = Field(default=None, description="Field names to order results by. Omit for the default ranking."),
        orderDirection: str | None = Field(default=None, description="Sort direction for orderBy (`asc` or `desc`). Omit for the server default."),
        slug: list[str] | None = Field(default=None, description="Tag slugs to filter by. Omit to not filter by slug."),
        ids: list[int] | None = Field(default=None, description="Tag IDs to filter by. Omit to not filter by ID."),
        parentId: int | None = Field(default=None, description="Return only children of this parent tag ID. parentSlug takes precedence if both are given. Omit to not filter by parent ID."),
        parentSlug: str | None = Field(default=None, description="Return only children of the parent tag with this slug. Takes precedence over parentId. Omit to not filter by parent slug."),
        query: str | None = Field(default=None, description="Case-insensitive substring to match against tag labels. Omit to not filter by label."),
    ) -> ListTagsResult:
        tlog = ToolLogger(logger, "list_tags")
        params = {
            "limit": limit,
            "offset": offset,
            "orderBy": orderBy,
            "orderDirection": orderDirection,
            "slug": slug,
            "ids": ids,
            "parentId": parentId,
            "parentSlug": parentSlug,
            "query": query,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v2/tags", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=False,
            )
            if 200 <= status < 300:
                result = ListTagsResult(success=True, statusCode=status, data=ListTagsData(**data))
                tlog.success()
                return result
            return _upstream_err(ListTagsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListTagsResult, tlog, exc)

    @mcp.tool(
        name="get_tag_by_slug",
        description=(
            "Gets a single tag by its slug. Returns the tag's ID, label, image, tradable flag, "
            "league and sport details, parent ID and subtags."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_tag_by_slug(
        slug: str = Field(description="Slug of the tag to retrieve (e.g. from list_tags)."),
    ) -> GetTagBySlugResult:
        tlog = ToolLogger(logger, "get_tag_by_slug")
        if not slug.strip():
            return _err(GetTagBySlugResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/tags/slug/{quote(slug, safe='')}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=False,
            )
            if 200 <= status < 300:
                if not data.get("tag"):
                    return _err(GetTagBySlugResult, tlog, "VALIDATION_ERROR",
                                f"No tag with slug `{slug}`", 404)
                result = GetTagBySlugResult(success=True, statusCode=status, data=GetTagBySlugData(**data))
                tlog.success()
                return result
            return _upstream_err(GetTagBySlugResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetTagBySlugResult, tlog, exc)

    @mcp.tool(
        name="get_tag_by_id",
        description=(
            "Gets a single tag by its numeric ID. Returns the tag's label, slug, image, tradable "
            "flag, league and sport details, parent ID and subtags."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_tag_by_id(
        tag_id: int = Field(description="Numeric ID of the tag to retrieve (the tag `id` from list_tags)."),
    ) -> GetTagByIdResult:
        tlog = ToolLogger(logger, "get_tag_by_id")
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/tags/{tag_id}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=False,
            )
            if 200 <= status < 300:
                if not data.get("tag"):
                    return _err(GetTagByIdResult, tlog, "VALIDATION_ERROR",
                                f"No tag with id `{tag_id}`", 404)
                result = GetTagByIdResult(success=True, statusCode=status, data=GetTagByIdData(**data))
                tlog.success()
                return result
            return _upstream_err(GetTagByIdResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetTagByIdResult, tlog, exc)

    @mcp.tool(
        name="list_tag_events",
        description=(
            "Lists events carrying a given tag slug, sorted by volume descending unless orderBy/"
            "orderDirection say otherwise. Returns each event's ID, ticker, slug, title, dates, "
            "status flags, liquidity and volume figures, markets, tags, teams and live game state. "
            "By default only active, non-closed events are returned; set active/closed to include others."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_tag_events(
        slug: str = Field(description="Slug of the tag whose events to list (e.g. from list_tags)."),
        limit: int | None = Field(default=None, description="Maximum number of events to return. Omit for the server default."),
        offset: int | None = Field(default=None, description="Number of events to skip for pagination. Omit to start from the first event."),
        orderBy: list[str] | None = Field(default=None, description="Field names to order results by. Omit to order by volume."),
        orderDirection: str | None = Field(default=None, description="Sort direction for orderBy (`asc` or `desc`). Omit for `desc`."),
        active: bool | None = Field(default=None, description="Filter by active status. Omit to return only active events (server default true)."),
        closed: bool | None = Field(default=None, description="Filter by closed status. Omit to exclude closed events (server default false)."),
    ) -> ListTagEventsResult:
        tlog = ToolLogger(logger, "list_tag_events")
        if not slug.strip():
            return _err(ListTagEventsResult, tlog, "VALIDATION_ERROR", "slug must not be empty", 400)
        params = {
            "limit": limit,
            "offset": offset,
            "orderBy": orderBy,
            "orderDirection": orderDirection,
            "active": active,
            "closed": closed,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/tags/{quote(slug, safe='')}/events", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), authenticated=False,
            )
            if 200 <= status < 300:
                result = ListTagEventsResult(success=True, statusCode=status, data=ListTagEventsData(**data))
                tlog.success()
                return result
            return _upstream_err(ListTagEventsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListTagEventsResult, tlog, exc)
