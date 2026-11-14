from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class IncentiveTimePeriod(BaseModel):
    model_config = ConfigDict(extra="allow")

    programId: str | None = None
    programType: str | None = Field(default=None, description="Program type, e.g. liquidityProgram or volumeProgram.")
    start: str | None = None
    end: str | None = None
    rewardPool: float | None = None
    status: str | None = None
    discountFactor: float | None = None
    targetSize: int | None = None
    maxSpread: float | None = Field(default=None, description=(
        "Liquidity programs only: half-width in price dollars from mid (0.035 = 3.5 cents). "
        "Omitted when the program has no max spread."
    ))
    period: str | None = None
    createdAt: str | None = None
    minTakerNotional: int | None = None


class IncentiveProgram(BaseModel):
    model_config = ConfigDict(extra="allow")

    marketSlug: str | None = None
    timePeriods: list[IncentiveTimePeriod] = Field(default_factory=list)
    instrumentState: str | None = Field(default=None, description=(
        "INSTRUMENT_STATE_OPEN, _PREOPEN, _SUSPENDED, _EXPIRED, _TERMINATED, _HALTED, "
        "_MATCH_AND_CLOSE_AUCTION or _PENDING."
    ))
    category: str | None = None
    subcategory: str | None = None
    eventStartTime: str | None = None
    instrumentProduct: str | None = None


class ListIncentiveProgramsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    programs: list[IncentiveProgram] = Field(default_factory=list)
    nextPageToken: str | None = Field(default=None, description="Pass as `page_token` to fetch the next page, if more results exist.")


class ListIncentiveProgramsResult(ToolResult):
    data: ListIncentiveProgramsData | None = None


class IncentiveReward(BaseModel):
    model_config = ConfigDict(extra="allow")

    reward: float | None = None
    programType: str | None = None
    marketSlug: str | None = None
    date: str | None = Field(default=None, description="Eastern Time date the payouts are summed for.")
    status: str | None = None


class ListIncentiveEarningsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    rewards: list[IncentiveReward] = Field(default_factory=list)


class ListIncentiveEarningsResult(ToolResult):
    data: ListIncentiveEarningsData | None = None
