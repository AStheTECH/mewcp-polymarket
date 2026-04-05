# Polymarket MCP Server

A Model Context Protocol (MCP) server that provides access to Polymarket's prediction market APIs.

## Authentication

The Polymarket API has three components:

- **Gamma API** (market/event data): No authentication required
- **Data API** (user positions/trades): No authentication required  
- **CLOB API** (orderbook/prices): No authentication for public endpoints, **API key required** for trading

**Auth Model**: For authenticated operations (order creation, cancellation), API key must be provided with every tool call. The server is stateless and does not store authentication credentials between requests.

**MCP Type**: Third-party integration (auth required for trading operations only)

## Available Tools

### Market Data (Gamma API - No Auth)

#### `polymarket_get_markets`
Get list of markets from Polymarket.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `limit` | integer | ❌ No | Maximum markets to return (1-1000, default: 100) |
| `offset` | integer | ❌ No | Skip N markets for pagination (default: 0) |
| `active` | boolean | ❌ No | Filter by active status |

#### `polymarket_get_market`
Get detailed information about a specific market by ID.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `market_id` | string | ✅ Yes | Market ID to retrieve |

#### `polymarket_get_events`
Get list of events from Polymarket.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `limit` | integer | ❌ No | Maximum events to return (1-1000, default: 100) |
| `offset` | integer | ❌ No | Skip N events for pagination (default: 0) |

### User Data (Data API - No Auth)

#### `polymarket_get_user_positions`
Get user positions by wallet address.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `user_address` | string | ✅ Yes | Ethereum wallet address to query |

#### `polymarket_get_user_trades`
Get user trade history by wallet address.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `user_address` | string | ✅ Yes | Ethereum wallet address to query |
| `limit` | integer | ❌ No | Maximum trades to return (1-1000, default: 100) |
| `offset` | integer | ❌ No | Skip N trades for pagination (default: 0) |

### Orderbook Data (CLOB API - No Auth)

#### `polymarket_get_orderbook`
Get orderbook for a specific market.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `market_id` | string | ✅ Yes | Market ID to get orderbook for |

#### `polymarket_get_midpoint`
Get midpoint price for a specific market.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `market_id` | string | ✅ Yes | Market ID to get midpoint for |

### Trading (CLOB API - Auth Required)

#### `polymarket_create_order`
Create a new order on Polymarket.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `api_key` | string | ✅ Yes | Polymarket API key |
| `market_id` | string | ✅ Yes | Market ID to place order on |
| `side` | string | ✅ Yes | 'BUY' or 'SELL' |
| `price` | float | ✅ Yes | Order price in USD |
| `size` | float | ✅ Yes | Order size (number of shares) |
| `token_id` | string | ✅ Yes | Token ID for the market outcome |

#### `polymarket_cancel_order`
Cancel an existing order.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `api_key` | string | ✅ Yes | Polymarket API key |
| `order_id` | string | ✅ Yes | ID of the order to cancel |

#### `polymarket_get_orders`
Get user's orders.

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `api_key` | string | ✅ Yes | Polymarket API key |
| `market_id` | string | ❌ No | Optional market ID to filter orders |

### Utility

#### `polymarket_health_check`
Check server readiness and basic connectivity.

**Arguments**: None

## Setup

```bash
# Clone the repository
git clone <repository-url>
cd cl-mcp-polymarket

# Install dependencies
pip install -r requirements.txt