from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class PendingWithdrawal(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str | None = Field(default=None, description="Account name.")
    balance: float | None = Field(default=None, description="Balance to withdraw.")
    description: str | None = None
    acknowledged: bool | None = None
    bankId: str | None = Field(default=None, description="Bank ID of the recipient.")
    creationTime: str | None = None
    destinationAccountName: str | None = None


class UserBalance(BaseModel):
    model_config = ConfigDict(extra="allow")

    currentBalance: float | None = Field(default=None, description="Current fiat balance, not including security values.")
    currency: str | None = None
    lastUpdated: str | None = None
    buyingPower: float | None = Field(default=None, description="Unencumbered capital available for trading, factoring in security valuations and open orders.")
    assetNotional: float | None = Field(default=None, description="Aggregate notional value of all securities.")
    assetAvailable: float | None = Field(default=None, description="Aggregate available collateral value of all securities.")
    pendingCredit: float | None = Field(default=None, description="Aggregate value of all pending credits.")
    openOrders: float | None = Field(default=None, description="Aggregate notional value of open orders.")
    unsettledFunds: float | None = Field(default=None, description="Aggregate notional value of unsettled funds not yet available to trade.")
    pendingWithdrawals: list[PendingWithdrawal] = Field(default_factory=list)
    marginRequirement: float | None = Field(default=None, description="Aggregate margin requirement for event instrument positions.")
    balanceReservation: float | None = Field(default=None, description="Aggregate notional value of balance reservations.")


class GetAccountBalancesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    balances: list[UserBalance] = Field(default_factory=list, description="Balances, one per currency.")


class GetAccountBalancesResult(ToolResult):
    data: GetAccountBalancesData | None = None
