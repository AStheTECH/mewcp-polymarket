from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class Series(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    recurrence: str | None = None
    image: str | None = None
    active: bool | None = None
    createdAt: str | None = None
    updatedAt: str | None = None


class ListSeriesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    series: list[Series] = []


class ListSeriesResult(ToolResult):
    data: ListSeriesData | None = None


class GetSeriesByIdData(BaseModel):
    model_config = ConfigDict(extra="allow")

    series: Series | None = None


class GetSeriesByIdResult(ToolResult):
    data: GetSeriesByIdData | None = None
