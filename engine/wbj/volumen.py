"""Lector de volumen automático — el juez final de las entradas de Tania.

Regla de Tania: sin volumen no hay entrada ([[regla-volumen-obligatorio]]). Antes
ella lo confirmaba a ojo; ahora se mide con datos de Schwab.

`volumen_estado` baja las barras intradía (Schwab pricehistory) y decide si el
volumen está ELEVADO ahora mismo vs su base del día. El SPX es un índice sin
volumen negociable propio, así que se usa **SPY** como proxy (el ETF que sí
cotiza). Para acciones, la propia acción.

Nota honesta: esto es un proxy sólido de "hay esfuerzo en el nivel" (volumen
elevado), no el VSA completo de Wyckoff (volumen + spread + cierre). Da un sí/no
con dato, en vez de adivinar; la lectura fina del gráfico sigue sumando.
"""

from __future__ import annotations

import statistics

_PRICEHISTORY = "https://api.schwabapi.com/marketdata/v1/pricehistory"

# Índices → su ETF negociable (donde vive el volumen real).
_PROXY = {"SPX": "SPY", "$SPX": "SPY", "NDX": "QQQ", "$NDX": "QQQ",
          "RUT": "IWM", "$RUT": "IWM", "$VIX": "VXX"}

# Umbral: cuántas veces el volumen base cuenta como "elevado".
FACTOR_ELEVADO = 1.5


def proxy_de(symbol: str) -> str:
    """El símbolo con volumen negociable (SPY para SPX, etc.)."""
    return _PROXY.get(symbol.upper(), symbol.upper().lstrip("$"))


def volumen_estado(symbol: str, schwab, frecuencia: int = 5) -> dict:
    """¿El volumen está elevado ahora? Usa barras intradía de Schwab.

    Devuelve {simbolo, ultima, base, ratio, elevado, barras} o {"error": ...}.
    `elevado` = última barra >= FACTOR_ELEVADO × base (mediana del día).
    """
    prox = proxy_de(symbol)
    try:
        tok = schwab._valid_access_token()
        if not tok:
            return {"error": "Schwab no autorizado"}
        import httpx
        r = schwab.client.get(
            _PRICEHISTORY,
            headers={"Authorization": f"Bearer {tok}"},
            params={"symbol": prox, "periodType": "day", "period": "1",
                    "frequencyType": "minute", "frequency": str(frecuencia),
                    "needExtendedHoursData": "false"},
        )
        if r.status_code != 200:
            return {"error": f"pricehistory {r.status_code}"}
        candles = r.json().get("candles", [])
    except (httpx.HTTPError, ValueError, AttributeError) as e:
        return {"error": f"{type(e).__name__}"}

    vols = [c.get("volume", 0) for c in candles if c.get("volume")]
    if len(vols) < 5:
        return {"error": "sin barras suficientes (¿mercado cerrado?)"}
    ultima = float(vols[-1])
    base = float(statistics.median(vols[:-1]))  # base = mediana sin la última
    ratio = ultima / base if base > 0 else 0.0
    return {
        "simbolo": prox, "ultima": round(ultima), "base": round(base),
        "ratio": round(ratio, 2), "elevado": ratio >= FACTOR_ELEVADO,
        "barras": len(vols),
        "detalle": f"{prox}: última barra {ultima:,.0f} vs base {base:,.0f} "
                   f"= {ratio:.1f}× ({'ELEVADO' if ratio >= FACTOR_ELEVADO else 'normal/bajo'})",
    }
