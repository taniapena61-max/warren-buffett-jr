"""EMA-200 discount screen — Tania's entry strategy, as an add-on to the brain.

Tania buys quality companies trading *below* their 200-day EMA (a technical
discount) and exits at +25%. This module is additive: it reuses Victor's own
EMA (`wbj.engines.indicators.ema`, TECH-EMA-003) and screener, and never
modifies them.

Two pieces:
- `ema200_status(ticker, price)` — where the price sits vs its 200-day EMA,
  from keyless Yahoo daily closes (so screening many names doesn't burn the
  FMP quota).
- `discount_screen(...)` — runs the discovery screener, then keeps only names
  under their EMA200 (a real discount) with a minimum quality score, so a
  cheap-but-broken value trap is filtered out rather than surfaced.

"Below EMA200" is a *timing* discount, never a buy order — every row is
research classification, consistent with the Cerebro's rules.
"""

from __future__ import annotations

import httpx
import pandas as pd

from wbj.engines.indicators import ema

_YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{t}"
_YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0 warren-buffett-jr"}
TAKE_PROFIT = 0.25  # Tania's fixed exit target.


def _daily_closes_yahoo(ticker: str, client: httpx.Client | None = None) -> list[float]:
    """~2y of adjusted daily closes from Yahoo (keyless). [] on failure."""
    own = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        r = client.get(
            _YAHOO_URL.format(t=ticker.upper()),
            params={"range": "2y", "interval": "1d"},
            headers=_YAHOO_HEADERS,
        )
        if r.status_code != 200:
            return []
        res = r.json()["chart"]["result"][0]
        adj = res["indicators"]["adjclose"][0]["adjclose"]
        return [c for c in adj if isinstance(c, (int, float))]
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return []
    finally:
        if own:
            client.close()


def ema200_status(
    ticker: str, price: float | None, client: httpx.Client | None = None
) -> dict:
    """Where `price` sits vs the 200-day EMA (TECH-EMA-003, Victor's engine).

    Returns {ema200, below_ema200, discount, take_profit_25}; `discount` is
    negative when the price is under the EMA (a discount). Fields are None
    when history is too short (<200 sessions) or unavailable.
    """
    empty = {"ema200": None, "below_ema200": None, "discount": None, "take_profit_25": None}
    if price is None:
        return empty
    closes = _daily_closes_yahoo(ticker, client)
    if len(closes) < 200:
        return empty
    ema_series = ema(pd.Series(closes, dtype=float), 200)
    if ema_series.dropna().empty:
        return empty
    e = float(ema_series.iloc[-1])
    return {
        "ema200": round(e, 2),
        "below_ema200": price < e,
        "discount": round((price - e) / e, 4),  # <0 = below EMA200
        "take_profit_25": round(price * (1 + TAKE_PROFIT), 2),
    }


def discount_screen(limit: int = 15, min_score: float = 6.5, progress=None) -> list[dict]:
    """Discovery screener filtered to Tania's criterion: under EMA200 AND a
    minimum quality score (guards against value traps).

    Reuses `wbj.screener.screen` (Victor's) unchanged, then enriches and
    filters. Returns rows sorted by discount (deepest first).
    """
    from wbj.screener import screen as run_screen

    rows = run_screen(limit=40, progress=progress)
    client = httpx.Client(timeout=10.0)
    out: list[dict] = []
    try:
        for r in rows:
            if r.get("score10") is None or r["score10"] < min_score:
                continue
            st = ema200_status(r["ticker"], r.get("price"), client=client)
            if not st["below_ema200"]:
                continue
            out.append({**r, **st})
    finally:
        client.close()
    out.sort(key=lambda r: r["discount"])
    return out[:limit]
