**Browse prediction markets, track positions, and place trades on Polymarket through AI.**

A Model Context Protocol (MCP) server that exposes Polymarket's API for querying markets, events, orderbooks, and user activity — with optional trading via the CLOB API.


## Overview

The Polymarket MCP Server provides full access to Polymarket's prediction market data and trading infrastructure:

- Browse active markets and events, inspect orderbooks and price history
- Look up any wallet's positions and trade history on-chain
- Place, cancel, and manage orders on the central limit order book (requires API key)

Perfect for:

- Building AI-powered market research tools that surface real-time prediction market data
- Monitoring portfolio positions and trade history by wallet address
- Automating trading strategies on Polymarket through natural language instructions


## Tools

<details>
<summary><code>polymarket_health_check</code> — Check server readiness</summary>

Returns a status object confirming the server is running and reachable.

**Inputs:** _(none)_

**Output:**

```json
{
  "status": "ok",
  "server": "CL Polymarket MCP Server"
}
```

</details>


<details>
<summary><code>polymarket_get_markets</code> — List prediction markets</summary>

Returns a paginated list of Polymarket markets with question, status, and end date. No API key required.

**Inputs:**
```
- `limit`  (integer, optional) — Maximum number of markets to return, 1–1000 (default: 100)
- `offset` (integer, optional) — Number of markets to skip for pagination (default: 0)
- `active` (boolean, optional) — Filter by active status
```

**Output:**

```json
{
  "success": true,
  "count": 10,
  "markets": [
    {
      "id": "0xabc...",
      "question": "Will X happen by 2025?",
      "active": true,
      "closed": false,
      "end_date": "2025-12-31T00:00:00Z"
    }
  ]
}
```

</details>


<details>
<summary><code>polymarket_get_market</code> — Get a specific market</summary>

Returns full details for a single market including condition ID, slug, tokens, and market type. No API key required.

**Inputs:**
```
- `market_id` (string, required) — Market ID to retrieve
```

**Output:**

```json
{
  "success": true,
  "market": {
    "id": "0xabc...",
    "question": "Will X happen?",
    "condition_id": "0xdef...",
    "slug": "will-x-happen",
    "end_date": "2025-12-31T00:00:00Z",
    "active": true,
    "closed": false,
    "market_type": "binary",
    "tokens": [...]
  }
}
```

</details>


<details>
<summary><code>polymarket_get_events</code> — List events</summary>

Returns a paginated list of events. Events group related markets together (e.g. all markets for an election). No API key required.

**Inputs:**
```
- `limit`  (integer, optional) — Maximum number of events to return, 1–1000 (default: 100)
- `offset` (integer, optional) — Number of events to skip for pagination (default: 0)
```

**Output:**

```json
{
  "success": true,
  "count": 5,
  "events": [
    {
      "id": "123",
      "title": "2025 US Election",
      "slug": "2025-us-election",
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-11-05T00:00:00Z"
    }
  ]
}
```

</details>


<details>
<summary><code>polymarket_get_user_positions</code> — Get positions for a wallet</summary>

Returns all open positions held by an Ethereum wallet address. No API key required.

**Inputs:**
```
- `user_address` (string, required) — Ethereum wallet address to query
```

**Output:**

```json
{
  "success": true,
  "user_address": "0x123...",
  "count": 3,
  "positions": [
    {
      "position_id": "pos_1",
      "asset": "0xabc...",
      "quantity": 100.0,
      "average_price": 0.65,
      "current_value": 72.50
    }
  ]
}
```

</details>


<details>
<summary><code>polymarket_get_user_trades</code> — Get trade history for a wallet</summary>

Returns the full trade history for an Ethereum wallet address, paginated. No API key required.

**Inputs:**
```
- `user_address` (string, required)  — Ethereum wallet address to query
- `limit`        (integer, optional) — Maximum number of trades to return, 1–1000 (default: 100)
- `offset`       (integer, optional) — Number of trades to skip for pagination (default: 0)
```

**Output:**

```json
{
  "success": true,
  "user_address": "0x123...",
  "count": 25,
  "trades": [
    {
      "id": "trade_1",
      "market": "0xabc...",
      "outcome": "YES",
      "side": "BUY",
      "size": 50.0,
      "price": 0.62,
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
}
```

</details>


<details>
<summary><code>polymarket_get_orderbook</code> — Get orderbook for a market</summary>

Returns the current bids and asks for a market from the central limit order book. No API key required.

**Inputs:**
```
- `market_id` (string, required) — Market ID to get orderbook for
```

**Output:**

```json
{
  "success": true,
  "market": "0xabc...",
  "bids": [[0.62, 500], [0.61, 1200]],
  "asks": [[0.63, 300], [0.64, 800]],
  "timestamp": "2025-01-01T12:00:00Z"
}
```

</details>


<details>
<summary><code>polymarket_get_midpoint</code> — Get midpoint price for a market</summary>

Returns the midpoint price (average of best bid and best ask) for a market. No API key required.

**Inputs:**
```
- `market_id` (string, required) — Market ID to get midpoint for
```

**Output:**

```json
{
  "success": true,
  "market": "0xabc...",
  "midpoint": 0.625,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

</details>


<details>
<summary><code>polymarket_create_order</code> — Place an order on the CLOB</summary>

Creates a new limit order on Polymarket's central limit order book. Requires an API key with trading permissions.

**Inputs:**
```
- `market_id` (string, required) — Market ID to place order on
- `side`      (string, required) — Order side: 'BUY' or 'SELL'
- `price`     (float, required)  — Order price in USD (0–1 for binary markets)
- `size`      (float, required)  — Order size in number of shares
- `token_id`  (string, required) — Token ID for the market outcome
```

**Output:**

```json
{
  "success": true,
  "order_id": "order_abc123",
  "market": "0xabc...",
  "side": "BUY",
  "price": 0.62,
  "size": 100.0,
  "status": "OPEN"
}
```

</details>


<details>
<summary><code>polymarket_cancel_order</code> — Cancel an open order</summary>

Cancels an existing open order on the CLOB. Requires an API key with trading permissions.

**Inputs:**
```
- `order_id` (string, required) — ID of the order to cancel
```

**Output:**

```json
{
  "success": true,
  "order_id": "order_abc123",
  "message": "Order cancelled successfully"
}
```

</details>


<details>
<summary><code>polymarket_get_orders</code> — Get your open orders</summary>

Returns all open orders for the authenticated account, optionally filtered by market. Requires an API key.

**Inputs:**
```
- `market_id` (string, optional) — Filter orders by market ID
```

**Output:**

```json
{
  "success": true,
  "count": 2,
  "orders": [
    {
      "id": "order_abc123",
      "market": "0xabc...",
      "side": "BUY",
      "price": 0.62,
      "size": 100.0,
      "status": "OPEN",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Common Parameters</strong></summary>

- `limit` — Maximum number of records to return per request (max 1000, default 100)
- `offset` — Number of records to skip; use with `limit` for pagination
- `market_id` — A market's on-chain condition ID or internal ID, returned by `polymarket_get_markets`

</details>

<details>
<summary><strong>Resource Formats</strong></summary>

**Market ID:**

```
Ethereum condition ID (hex string)
Example: 0x1234567890abcdef...
```

**Wallet Address:**

```
Ethereum address (checksummed or lowercase)
Example: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Price:**

```
Decimal between 0 and 1 representing implied probability
Example: 0.65  (65% probability = $0.65 per share)
```

</details>

<details>
<summary><strong>Trading Notes</strong></summary>

- `polymarket_create_order`, `polymarket_cancel_order`, and `polymarket_get_orders` require an API key
- `token_id` is found in the `tokens` array of `polymarket_get_market` — each binary market has a YES and NO token
- Order `side` must be `'BUY'` or `'SELL'` (uppercase)
- All public read tools (markets, events, positions, trades, orderbook) work without an API key

</details>


## Getting Your Polymarket API Key

<details>
<summary><strong>Steps</strong></summary>

1. Go to the [Polymarket CLOB API documentation](https://docs.polymarket.com/#introduction)
2. Follow the authentication setup to derive your API key from your Ethereum wallet (EIP-712 signing)
3. The API key, secret, and passphrase are derived from a signed message — store all three securely
4. Use the `api_key` value when connecting your Polymarket credential in MewCP

> Polymarket's CLOB API uses a signature-based key derivation flow — keys are not issued through a web UI but generated by signing a message with your wallet.

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** API key not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_API_KEY` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check API key is active in your MewCP account

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No Polymarket credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Add your Polymarket API key (required only for trading tools)
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters are included
  3. For orders, confirm `side` is uppercase (`'BUY'` or `'SELL'`) and `price` is between 0 and 1

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>Polymarket API Error</strong></summary>

- **Cause:** Upstream Polymarket API returned an error
- **Solution:**
  1. Check Polymarket service status at [Polymarket Status](https://polymarket.com)
  2. Verify your API key has the required permissions for trading operations
  3. Review the error message for specific details (e.g. insufficient funds, market closed, invalid token ID)

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Polymarket CLOB API Documentation](https://docs.polymarket.com/#introduction)** — Official API reference
- **[Polymarket](https://polymarket.com/)** — Browse live markets
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling

</details>
