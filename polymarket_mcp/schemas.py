from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


# Gamma API Schemas
class Market(TypedDict, total=False):
    """Market information from Gamma API."""

    id: str
    question: str
    conditionId: str
    slug: str
    resolutionSource: str
    endDate: str
    active: bool
    closed: bool
    marketType: str
    tokens: List[Dict[str, Any]]


class Event(TypedDict, total=False):
    """Event information from Gamma API."""

    id: str
    title: str
    slug: str
    startDate: str
    endDate: str
    markets: List[Market]


# Data API Schemas
class Position(TypedDict, total=False):
    """User position from Data API."""

    positionId: str
    asset: str
    quantity: float
    averagePrice: float
    currentValue: float


class Trade(TypedDict, total=False):
    """Trade information from Data API."""

    id: str
    market: str
    outcome: str
    side: str
    size: float
    price: float
    timestamp: str


# CLOB API Schemas
class Orderbook(TypedDict, total=False):
    """Orderbook data from CLOB API."""

    market: str
    bids: List[List[float]]  # [price, size]
    asks: List[List[float]]  # [price, size]
    timestamp: str


class Order(TypedDict, total=False):
    """Order data for CLOB API."""

    id: str
    market: str
    side: str  # BUY or SELL
    price: float
    size: float
    status: str
    createdAt: str


class CreateOrderRequest(TypedDict, total=False):
    """Request to create an order."""

    market: str
    side: str
    price: float
    size: float
    tokenId: str
