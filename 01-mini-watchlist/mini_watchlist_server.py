"""
Mini Watchlist: a tiny remote MCP server for learning how Claude connectors work.

Run:   python mini_watchlist_server.py
Serves: http://localhost:8000/mcp   (Streamable HTTP transport)

Three tools, increasing in "realness":
  1. ping            - proves the connection works
  2. add_to_watchlist / remove_from_watchlist / get_watchlist
                     - stateful tools (in-memory, resets on restart)
  3. get_fake_quote  - shows how a tool would wrap an external data source
"""

import random
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP

# stateless_http=True: no per-session state held by the server, simplest to host/tunnel.
# host="0.0.0.0": needed so requests arriving via a tunnel (different Host header) are accepted.
mcp = FastMCP("mini-watchlist", host="0.0.0.0", port=8000, stateless_http=True)

# In-memory store. Swap for a file or DB when you want persistence.
WATCHLIST: set[str] = set()

IST = timezone(timedelta(hours=5, minutes=30))


@mcp.tool()
def ping() -> str:
    """Check that the connector is alive. Returns the current time in IST."""
    return f"pong from mini-watchlist at {datetime.now(IST):%Y-%m-%d %H:%M:%S} IST"


@mcp.tool()
def add_to_watchlist(symbols: list[str]) -> str:
    """Add one or more stock symbols (e.g. RELIANCE, TCS) to the watchlist."""
    added = [s.strip().upper() for s in symbols if s.strip()]
    WATCHLIST.update(added)
    return f"Added {added}. Watchlist now has {len(WATCHLIST)} symbol(s)."


@mcp.tool()
def remove_from_watchlist(symbols: list[str]) -> str:
    """Remove one or more stock symbols from the watchlist."""
    removed = [s.strip().upper() for s in symbols]
    WATCHLIST.difference_update(removed)
    return f"Removed {removed}. Watchlist now has {len(WATCHLIST)} symbol(s)."


@mcp.tool()
def get_watchlist() -> list[str]:
    """Return all symbols currently on the watchlist, sorted alphabetically."""
    return sorted(WATCHLIST)


@mcp.tool()
def get_fake_quote(symbol: str) -> dict:
    """Return a FAKE, randomly generated quote for a symbol. Demo only, not real data."""
    price = round(random.uniform(500, 3000), 2)
    return {
        "symbol": symbol.strip().upper(),
        "price": price,
        "currency": "INR",
        "note": "Randomly generated for the tutorial. Replace with a real data source.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
