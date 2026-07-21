"""Lee las alertas de MarketSnack y las cruza con el sistema de Tania.

Flujo:
  1. Lee los correos recientes de MarketSnack (Gmail IMAP, solo lectura).
  2. Extrae candidatos a ticker y los VALIDA contra el universo real de EDGAR
     (así "CEO", "USA", "AI" no se cuelan como tickers).
  3. Para cada ticker válido: estado vs EMA200 (criterio de descuento de Tania)
     y scorecard rápido (calidad) — para separar oportunidad de trampa.
  4. Imprime un tablero ordenado. MarketSnack aporta la señal de movimiento;
     el veredicto de oportunidad sale del sistema de Tania, no del newsletter.

Uso:
    python scripts/oportunidades_marketsnack.py            # analiza
    python scripts/oportunidades_marketsnack.py --remitentes  # lista remitentes
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wbj.config import load_settings  # noqa: E402
from wbj.providers.gmail_imap import leer_marketsnack, remitentes_recientes  # noqa: E402

# Palabras en mayúsculas que NO son tickers aunque lo parezcan.
_STOP = {
    "CEO", "CFO", "CTO", "COO", "USA", "US", "UK", "EU", "AI", "ML", "IPO", "ETF",
    "GDP", "CPI", "FED", "SEC", "FDA", "EPS", "PE", "YOY", "Q1", "Q2", "Q3", "Q4",
    "AM", "PM", "EST", "ET", "NYSE", "OK", "TV", "CEO'S", "API", "EV", "SUV",
    "THE", "AND", "FOR", "NEW", "NOW", "BUY", "ALL", "GET", "TOP", "WSJ", "COVID",
}


def _cargar_tickers_validos(settings) -> set[str]:
    """Universo de tickers reales desde EDGAR (cache-first)."""
    from wbj.providers.edgar import (TICKERS_URL, _EDGAR_HEADERS,
                                     _GLOBAL_CACHE_TICKER, _MAX_AGE_TICKERS,
                                     EdgarProvider)
    edgar = EdgarProvider(settings.cache_dir)
    data = edgar.get_json(TICKERS_URL, {}, "tickers", _GLOBAL_CACHE_TICKER,
                          max_age_days=_MAX_AGE_TICKERS, headers=_EDGAR_HEADERS) or {}
    return {e["ticker"].upper() for e in data.values()
            if isinstance(e, dict) and e.get("ticker")}


def extraer_tickers(texto: str, validos: set[str]) -> list[str]:
    """Saca candidatos ($XXX o (XXX)) y los filtra contra el universo real."""
    cands = set()
    cands.update(m.upper() for m in re.findall(r"\$([A-Za-z]{1,5})\b", texto))
    cands.update(m.upper() for m in re.findall(r"\(([A-Z]{1,5})\)", texto))
    # también "Nvidia (NVDA)" ya cubierto por el patrón de paréntesis
    return sorted(t for t in cands if t not in _STOP and t in validos)


def main() -> int:
    settings = load_settings()
    addr = getattr(settings, "gmail_address", None)
    pwd = getattr(settings, "gmail_app_password", None)
    sender = getattr(settings, "marketsnack_sender", None)

    if "--remitentes" in sys.argv:
        r = remitentes_recientes(addr, pwd)
        if r.get("error"):
            print("Error:", r["error"]); return 1
        print("Remitentes recientes en tu bandeja (para identificar MarketSnack):\n")
        for frm, asunto in r["remitentes"].items():
            print(f"  {frm}\n     └ {asunto[:70]}")
        return 0

    r = leer_marketsnack(addr, pwd, remitente=sender, dias=7, limite=8)
    if r.get("error"):
        print("Error:", r["error"]); return 1
    msgs = r["mensajes"]
    if not msgs:
        print("No encontré correos de MarketSnack en los últimos 7 días.")
        print("Prueba: python scripts/oportunidades_marketsnack.py --remitentes")
        return 0

    print(f"Leídos {len(msgs)} correos de MarketSnack.\n")
    validos = _cargar_tickers_validos(settings)

    tickers: dict[str, str] = {}  # ticker -> asunto donde apareció
    for m in msgs:
        for t in extraer_tickers(m.texto + " " + m.asunto, validos):
            tickers.setdefault(t, (m.fecha.strftime("%d-%b") if m.fecha else "") +
                               " · " + m.asunto[:50])
    if not tickers:
        print("No detecté tickers reconocibles en esos correos.")
        return 0

    print(f"Tickers mencionados: {', '.join(sorted(tickers))}\n")
    print("Cruzando con tu sistema (EMA200 + calidad)...\n")

    import httpx
    from wbj.cli import _build_packet
    from wbj.ema_discount import ema200_status
    from wbj.quick import quick_scorecard
    from wbj.targets import live_price

    client = httpx.Client(timeout=12.0)
    filas = []
    for t in sorted(tickers):
        try:
            px = live_price(t, fmp_api_key=settings.fmp_api_key, client=client)
            st = ema200_status(t, px, client=client)
            sc = None
            try:
                sc = quick_scorecard(_build_packet(t)).get("overall_10")
            except Exception:  # noqa: BLE001
                pass
            filas.append({"t": t, "px": px, "ema": st["ema200"],
                          "bajo": st["below_ema200"], "desc": st["discount"],
                          "score": sc, "ctx": tickers[t]})
        except Exception:  # noqa: BLE001
            filas.append({"t": t, "px": None, "ema": None, "bajo": None,
                          "desc": None, "score": None, "ctx": tickers[t]})
    client.close()

    # oportunidades primero: bajo EMA200 y con calidad
    def rank(f):
        op = 1 if (f["bajo"] and (f["score"] or 0) >= 6.5) else 0
        return (op, -(f["desc"] if f["desc"] is not None else 0))
    filas.sort(key=rank, reverse=True)

    print(f"{'TICKER':<7}{'PRECIO':>9}{'EMA200':>9}{'DESC':>8}{'CALIDAD':>9}  SEÑAL")
    print("-" * 72)
    for f in filas:
        px = f"{f['px']:.2f}" if f["px"] else "n/d"
        ema = f"{f['ema']:.2f}" if f["ema"] else "n/d"
        desc = f"{f['desc']*100:+.1f}%" if f["desc"] is not None else "n/d"
        sc = f"{f['score']}/10" if f["score"] is not None else "n/d"
        marca = ""
        if f["bajo"] and (f["score"] or 0) >= 6.5:
            marca = "  ← OPORTUNIDAD (bajo EMA200 + calidad)"
        elif f["bajo"]:
            marca = "  · bajo EMA200 (revisar calidad)"
        print(f"{f['t']:<7}{px:>9}{ema:>9}{desc:>8}{sc:>9}{marca}")

    print("\nMarketSnack marca el movimiento; el veredicto de oportunidad es de tu "
          "sistema. Ninguna fila es orden de compra — es research para tu decisión.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
