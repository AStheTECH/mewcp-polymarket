from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class AssetId(BaseModel):
    model_config = ConfigDict(extra="allow")

    assetClass: str | None = Field(default=None, description="ASSET_CLASS_CRYPTO or ASSET_CLASS_COMMODITY.")
    symbol: str | None = Field(default=None, description="Lower-case symbol within the class, e.g. btc or gold.")


class AssetPriceCandle(BaseModel):
    model_config = ConfigDict(extra="allow")

    timestamp: int | None = Field(default=None, description="Bucket start (unix seconds).")
    open: str | None = Field(default=None, description="First price in the bucket, as a decimal string in the series currency.")
    high: str | None = Field(default=None, description="Highest price in the bucket, as a decimal string in the series currency.")
    low: str | None = Field(default=None, description="Lowest price in the bucket, as a decimal string in the series currency.")
    close: str | None = Field(default=None, description="Last price in the bucket, as a decimal string in the series currency; carried forward from the previous bucket when the bucket had no ticks.")
    tickCount: int | None = Field(default=None, description="Number of index ticks in the bucket. 0 marks a gap-filled bucket whose open/high/low equal its close.")


class AssetPriceSeries(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True, serialize_by_alias=True)

    asset: AssetId | None = None
    currency: str | None = Field(default=None, description="ISO 4217 currency code every candle price is quoted in.")
    bucket: str | None = Field(default=None, description="Candle width, e.g. ASSET_PRICE_BUCKET_1M.")
    from_: int | None = Field(default=None, alias="from", description="Effective window start (unix seconds) after alignment and clamping.")
    to: int | None = Field(default=None, description="Effective window end (unix seconds) after clamping.")
    candles: list[AssetPriceCandle] = Field(default=[], description="Dense ascending candles, one per bucket in the effective window. Empty when the asset has no data.")


class GetAssetPriceHistoryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    series: list[AssetPriceSeries] = Field(default=[], description="One series per distinct requested asset. Match by the asset field, never by position: the order is not guaranteed.")


class GetAssetPriceHistoryResult(ToolResult):
    data: GetAssetPriceHistoryData | None = None
