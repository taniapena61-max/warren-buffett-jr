"""Victor-style momentum screen — the inverse of the EMA200 discount screen.

Tania's EMA200 screen ([[ema_discount]]) buys weakness below the 200-day
average. Victor's methodology rewards the opposite: sustained strength. This
module implements the **primary-trend anchor table** from
`Cerebro/04_technical_momentum/DECISION_RULES.md` verbatim, using Victor's own
indicators (`wbj.engines.indicators`), and screens the quality universe for
names in a confirmed uptrend.

Scope, stated honestly: `trend_score` is ONLY the primary-trend anchor (the
first table in Victor's decision rules). His full 20-point Technical score also
weighs support/resistance zones, volume profile, anchored VWAP and breakout
state, which this module does not compute. So a high trend score here is
*necessary but not sufficient* for his "Momentum Candidate" gate — it is
timing evidence to investigate, never a verdict.

Price history comes from Yahoo (keyless OHLCV), because the FMP free tier
returns too little history to score technicals for most tickers.
"""

from __future__ import annotations

import httpx
import pandas as pd

from wbj.engines.indicators import adx14, atr14, range_position_52w, sma

_YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{t}"
_YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0 warren-buffett-jr"}

# Victor's anchor thresholds (DECISION_RULES.md, primary-trend table).
ADX_STRONG = 25.0
POS52_STRONG = 0.80
SLOPE_WINDOW = 50  # sessions over which the SMA200 slope is measured, in ATR


def daily_ohlcv_yahoo(ticker: str, client: httpx.Client | None = None) -> pd.DataFrame:
    """~2y of daily OHLCV from Yahoo. Empty frame on failure.

    ATR and ADX need high/low, so adjusted closes alone are not enough here.
    """
    own = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        r = client.get(
            _YAHOO_URL.format(t=ticker.upper()),
            params={"range": "2y", "interval": "1d"},
            headers=_YAHOO_HEADERS,
        )
        if r.status_code != 200:
            return pd.DataFrame()
        res = r.json()["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        df = pd.DataFrame({
            "high": q["high"], "low": q["low"],
            "close": q["close"], "volume": q["volume"],
        }).dropna()
        return df.reset_index(drop=True)
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return pd.DataFrame()
    finally:
        if own:
            client.close()


def trend_score(df: pd.DataFrame) -> dict:
    """Victor's primary-trend anchor score (0-10) plus its components.

    Evaluated strongest-first, since the anchor table's conditions overlap.
    Returns score=None when history is too short to judge (never a guess).
    """
    empty = {"score": None, "band": "sin datos", "close": None, "sma50": None,
             "sma200": None, "slope200_atr": None, "adx": None, "pos52": None}
    if len(df) < 252:  # need a year for the 52-week position and a stable SMA200
        return empty

    close = df["close"]
    s50, s200 = sma(close, 50), sma(close, 200)
    a, adx, pos = atr14(df), adx14(df), range_position_52w(df)
    if s200.dropna().empty or a.dropna().empty:
        return empty

    c = float(close.iloc[-1])
    m50, m200 = float(s50.iloc[-1]), float(s200.iloc[-1])
    atr_now = float(a.iloc[-1])
    if atr_now <= 0:
        return empty

    # Slopes over the last 50 sessions, expressed in ATR units (Victor's unit).
    sl200 = (m200 - float(s200.iloc[-1 - SLOPE_WINDOW])) / atr_now
    sl50 = (m50 - float(s50.iloc[-1 - SLOPE_WINDOW])) / atr_now
    adx_now = float(adx.iloc[-1]) if not adx.dropna().empty else None
    pos_now = float(pos.iloc[-1]) if not pos.dropna().empty else None

    stacked_up = c > m50 > m200 and sl50 > 0 and sl200 > 0
    if stacked_up and adx_now is not None and pos_now is not None \
            and adx_now >= ADX_STRONG and pos_now >= POS52_STRONG:
        score, band = 9.0, "liderazgo (9-10)"
    elif stacked_up:
        score, band = 8.0, "tendencia alcista (8)"
    elif c > m200:
        score, band = 6.0, "sobre SMA200, SMA50 mixta (6)"
    elif abs(c - m200) <= atr_now and -0.25 <= sl200 <= 0.25:
        score, band = 4.5, "lateral en la SMA200 (4-5)"
    elif c < m50 < m200 and sl200 < -1.0:
        score, band = 1.0, "bajista roto (0-2)"
    else:
        score, band = 3.0, "bajo SMA200, mixta (3)"

    return {"score": score, "band": band, "close": round(c, 2),
            "sma50": round(m50, 2), "sma200": round(m200, 2),
            "slope200_atr": round(sl200, 2),
            "adx": round(adx_now, 1) if adx_now is not None else None,
            "pos52": round(pos_now, 3) if pos_now is not None else None}


def momentum_screen(limit: int = 15, universe: int = 120, min_trend: float = 8.0,
                    progress=None) -> list[dict]:
    """Quality universe (SEC prefilter) filtered to Victor's uptrend anchors.

    Cheap-first: trend is computed from Yahoo for the strongest fundamental
    candidates, and the expensive EDGAR scorecard runs only for those that
    actually pass the trend gate.
    """
    from datetime import date

    from wbj.cli import _build_packet, _providers
    from wbj.providers.edgar import (TICKERS_URL, _EDGAR_HEADERS,
                                     _GLOBAL_CACHE_TICKER, _MAX_AGE_TICKERS)
    from wbj.quick import quick_scorecard
    from wbj.screener import prefilter

    _settings, edgar, _fmp = _providers()
    candidates = prefilter(edgar, date.today().year - 1)
    tickers = edgar.get_json(TICKERS_URL, {}, "tickers", _GLOBAL_CACHE_TICKER,
                             max_age_days=_MAX_AGE_TICKERS,
                             headers=_EDGAR_HEADERS) or {}
    by_cik = {e["cik_str"]: e for e in tickers.values() if isinstance(e, dict)}

    out: list[dict] = []
    client = httpx.Client(timeout=10.0)
    try:
        for i, cand in enumerate(candidates[:universe]):
            entry = by_cik.get(cand["cik"])
            if entry is None:
                continue
            ticker = entry["ticker"]
            if progress:
                progress(i + 1, min(universe, len(candidates)), ticker)
            t = trend_score(daily_ohlcv_yahoo(ticker, client=client))
            if t["score"] is None or t["score"] < min_trend:
                continue
            try:
                sc = quick_scorecard(_build_packet(ticker))
            except Exception:
                continue
            out.append({
                "ticker": ticker,
                "name": entry.get("title", "").title(),
                "growth": round(cand["growth"], 4),
                "margin": round(cand["margin"], 4),
                "score10": sc.get("overall_10"),
                "evidence": sc.get("evidence_points_covered"),
                **t,
            })
    finally:
        client.close()
    out.sort(key=lambda r: (r["score"], r["score10"] or 0), reverse=True)
    return out[:limit]
