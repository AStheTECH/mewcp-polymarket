"""Series group: list_series, get_series_by_id"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.series import (
    GetSeriesByIdData,
    GetSeriesByIdResult,
    ListSeriesData,
    ListSeriesResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("polymarket-mcp.tools.series")

_PARAMS_NOTE = "The API documents this `params.`-prefixed parameter separately from the plain one and without a description."


def register_series_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_series",
        description=(
            "Lists series (e.g., NFL 2025-26 Season), optionally filtered by slug, active state or "
            "recurrence and paged with limit/offset. Returns each series' ID, slug, title, subtitle, "
            "recurrence, image, active flag and timestamps. The API accepts two parameter sets: plain "
            "ones (`limit`, `offset`, `orderBy`, `slug`, ...) and `params.`-prefixed ones (the `params_*` "
            "arguments, including category and tag filters), which the provider lists without descriptions."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_series(
        limit: int | None = Field(default=None, description="Pagination limit. Omit to use the API default."),
        offset: int | None = Field(default=None, description="Pagination offset. Omit to start from the first series."),
        order_by: list[str] | None = Field(default=None, description="Pagination order (field names; sent as repeated `orderBy` values). Omit for the API default order."),
        order_direction: str | None = Field(default=None, description="Pagination order direction. Omit for the API default."),
        slug: list[str] | None = Field(default=None, description="Series slug(s) to filter by (sent as repeated `slug` values). Omit to not filter by slug."),
        active: bool | None = Field(default=None, description="Whether series is active. Omit to return both active and inactive series."),
        recurrence: str | None = Field(default=None, description="Series recurrence pattern to filter by. Omit to not filter by recurrence."),
        params_limit: int | None = Field(default=None, description=f"Sent as `params.limit`; by name, a pagination limit. {_PARAMS_NOTE} Omit to leave unset."),
        params_offset: int | None = Field(default=None, description=f"Sent as `params.offset`; by name, a pagination offset. {_PARAMS_NOTE} Omit to leave unset."),
        params_order_by: list[str] | None = Field(default=None, description=f"Sent as repeated `params.orderBy` values; by name, the pagination order. {_PARAMS_NOTE} Omit to leave unset."),
        params_order_direction: str | None = Field(default=None, description=f"Sent as `params.orderDirection`; by name, the pagination order direction. {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_slug: list[str] | None = Field(default=None, description=f"Sent as repeated `params.seriesFilters.slug` values; by name, a series slug filter. {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_categories_ids: list[int] | None = Field(default=None, description=f"Sent as repeated `params.seriesFilters.categoriesIds` values; by name, a filter on category IDs (integers). {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_categories_labels: list[str] | None = Field(default=None, description=f"Sent as repeated `params.seriesFilters.categoriesLabels` values; by name, a filter on category labels. {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_query: str | None = Field(default=None, description=f"Sent as `params.seriesFilters.query`; by name, a series query string. {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_active: bool | None = Field(default=None, description=f"Sent as `params.seriesFilters.active`; by name, a filter on whether series is active. {_PARAMS_NOTE} Omit to leave unset."),
        params_series_filters_recurrence: str | None = Field(default=None, description=f"Sent as `params.seriesFilters.recurrence`; by name, a series recurrence pattern filter. {_PARAMS_NOTE} Omit to leave unset."),
        params_tags_filters_include_template: bool | None = Field(default=None, description=f"Sent as `params.tagsFilters.includeTemplate`; by name, a tag filter flag for including templates. {_PARAMS_NOTE} Omit to leave unset."),
        params_tags_filters_query: str | None = Field(default=None, description=f"Sent as `params.tagsFilters.query`; by name, a tag query string. {_PARAMS_NOTE} Omit to leave unset."),
    ) -> ListSeriesResult:
        tlog = ToolLogger(logger, "list_series")
        params = {
            "limit": limit,
            "offset": offset,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "slug": slug,
            "active": active,
            "recurrence": recurrence,
            "params.limit": params_limit,
            "params.offset": params_offset,
            "params.orderBy": params_order_by,
            "params.orderDirection": params_order_direction,
            "params.seriesFilters.slug": params_series_filters_slug,
            "params.seriesFilters.categoriesIds": params_series_filters_categories_ids,
            "params.seriesFilters.categoriesLabels": params_series_filters_categories_labels,
            "params.seriesFilters.query": params_series_filters_query,
            "params.seriesFilters.active": params_series_filters_active,
            "params.seriesFilters.recurrence": params_series_filters_recurrence,
            "params.tagsFilters.includeTemplate": params_tags_filters_include_template,
            "params.tagsFilters.query": params_tags_filters_query,
        }
        try:
            data, status, retry_after = service.api_request(
                "GET", "/v1/series", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ListSeriesResult(success=True, statusCode=status, data=ListSeriesData(**data))
            return _upstream_err(ListSeriesResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListSeriesResult, tlog, exc)

    @mcp.tool(
        name="get_series_by_id",
        description=(
            "Retrieves a single series by its numeric ID. Returns the series' ID, slug, title, subtitle, "
            "recurrence, image, active flag and timestamps."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_series_by_id(
        series_id: int = Field(description="Series ID (integer), e.g. the `id` of a series from list_series."),
    ) -> GetSeriesByIdResult:
        tlog = ToolLogger(logger, "get_series_by_id")
        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v1/series/id/{series_id}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetSeriesByIdResult(success=True, statusCode=status, data=GetSeriesByIdData(**data))
            return _upstream_err(GetSeriesByIdResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetSeriesByIdResult, tlog, exc)
