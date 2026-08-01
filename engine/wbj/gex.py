"""Cálculo propio del Net GEX y el MVC — para no depender de la herramienta ajena.

Los compañeros de Tania publican el **MVC** (Max Volume/Gamma Concentration) desde
una plataforma que ella no tiene. Este módulo lo **calcula desde cero** con la
cadena de opciones de Schwab (gamma + interés abierto por strike), así Tania deja
de depender de terceros.

Definiciones (calibrables contra el número de los compañeros):
- **GEX por strike** = gamma × OI × 100 × spot²  (calls +, puts −).
- **MVC** = strike con la mayor concentración de |GEX| (el pico del perfil).
- **Gamma flip** = strike donde el GEX acumulado cruza de negativo a positivo.

⚠️ PENDIENTE DE CALIBRAR (2026-07-29): la convención exacta (qué vencimientos
incluir, el signo del dealer, si el pico es de |GEX| o del GEX positivo) se ajusta
comparando la salida real contra el MVC que publican los compañeros varios días.
Hasta entonces, tratar el número como aproximado.
"""

from __future__ import annotations

from typing import Any


def _iter_contratos(exp_map: dict) -> list[dict]:
    """Aplana el callExpDateMap/putExpDateMap de Schwab a una lista de contratos.

    Formato Schwab: {"2026-07-29:0": {"7400.0": [ {contrato...} ], ...}, ...}
    """
    filas: list[dict] = []
    for _exp, strikes in (exp_map or {}).items():
        if not isinstance(strikes, dict):
            continue
        for _k, lista in strikes.items():
            for c in (lista or []):
                if isinstance(c, dict):
                    filas.append(c)
    return filas


def _num(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    # Schwab manda -999.0 / NaN para campos no disponibles.
    if v != v or v <= -999:
        return None
    return v


def net_gex_por_strike(chain: dict, spot: float,
                       solo_vencimiento: str | None = None) -> list[dict]:
    """GEX neto por strike desde la cadena de Schwab.

    `solo_vencimiento`: 'YYYY-MM-DD' para filtrar a un solo vencimiento (0DTE);
    None = agrega todos los vencimientos que traiga la cadena.
    Devuelve [{strike, gex, gamma_oi, call_oi, put_oi}] ordenado por strike.
    """
    calls = _iter_contratos(chain.get("callExpDateMap", {}))
    puts = _iter_contratos(chain.get("putExpDateMap", {}))
    por_strike: dict[float, dict] = {}
    factor = 100.0 * spot * spot  # escala GEX a $ por 1% de movimiento aparte

    def _acum(contratos: list[dict], signo: float) -> None:
        for c in contratos:
            if solo_vencimiento and str(c.get("expirationDate", "")).startswith(solo_vencimiento) is False:
                # Schwab a veces pone expirationDate como epoch; el filtro fino
                # se hace por from/to al pedir la cadena. Aquí no descartamos.
                pass
            strike = _num(c.get("strikePrice"))
            gamma = _num(c.get("gamma"))
            oi = _num(c.get("openInterest"))
            if strike is None or gamma is None or oi is None:
                continue
            d = por_strike.setdefault(strike, {"strike": strike, "gex": 0.0,
                                               "call_oi": 0.0, "put_oi": 0.0})
            d["gex"] += signo * gamma * oi * factor
            if signo > 0:
                d["call_oi"] += oi
            else:
                d["put_oi"] += oi

    _acum(calls, +1.0)
    _acum(puts, -1.0)
    filas = sorted(por_strike.values(), key=lambda r: r["strike"])
    for r in filas:
        r["gamma_oi"] = abs(r["gex"]) / factor if factor else 0.0
    return filas


def mvc(chain: dict, spot: float) -> dict:
    """Calcula MVC, gamma flip y muros desde la cadena de Schwab.

    Returns: {mvc, gamma_flip, call_wall, put_wall, perfil:[...], nota}.
    """
    perfil = net_gex_por_strike(chain, spot)
    if not perfil:
        return {"error": "cadena vacía o sin gamma/OI (¿Schwab caído?)"}

    # Muros: mayor GEX positivo (call wall) y más negativo (put wall).
    call_wall = max(perfil, key=lambda r: r["gex"])
    put_wall = min(perfil, key=lambda r: r["gex"])
    # MVC / Magnet = el pico de |GEX| DOMINANTE (la mayor concentración, sea call
    # o put). CALIBRADO en dos puntos el 2026-07-31 vs el heatmap de los compañeros:
    #   - 9:51 régimen gamma+ (SPX ~7448): su MVC = 7500 = pico positivo (call wall).
    #   - 10:08 régimen gamma- (SPX ~7407): su MVC = 7400 = pico negativo (put wall).
    # El imán MIGRA con el spot y salta de lado según el régimen; por eso es max(|gex|),
    # no siempre el call wall. (Mi "fix" de forzarlo al call wall fue un error por
    # comparar spots distintos — revertido.)
    pico = max(perfil, key=lambda r: abs(r["gex"]))

    # Gamma flip: strike donde el GEX acumulado (de abajo hacia arriba) cambia de
    # signo negativo a positivo.
    flip = None
    acum = 0.0
    prev = None
    for r in perfil:
        acum += r["gex"]
        if prev is not None and prev < 0 <= acum:
            flip = r["strike"]
            break
        prev = acum

    # Net GEX total en la escala "por 1% de movimiento" (la que usa MarketSnack).
    # `factor` en net_gex_por_strike es 100*spot² (por $1); el 1% agrega *0.01.
    net_gex = sum(x["gex"] for x in perfil) * 0.01

    return {
        "mvc": pico["strike"],
        "mvc_gex": pico["gex"],
        "net_gex": net_gex,
        "gamma_flip": flip,
        "call_wall": call_wall["strike"],
        "put_wall": put_wall["strike"],
        "spot": spot,
        "perfil": perfil,
        "nota": ("CALIBRADO 2026-07-31 vs heatmap de compañeros en DOS regímenes: "
                 "gamma+ (SPX~7448) su MVC=7500=call wall; gamma- (SPX~7407) su "
                 "MVC=7400=put wall. Mi max(|gex|) reprodujo ambos. Los muros son "
                 "sólidos. El gamma_flip de esta función (GEX acumulado) es CRUDO — "
                 "para el flip fino usar gamma_flip.py (Black-Scholes)."),
    }


def calcular_mvc(symbol: str, sch, fecha: str | None = None,
                 strike_count: int = 80) -> dict:
    """Baja la cadena de Schwab y devuelve el MVC. `sch` = SchwabProvider.

    fecha 'YYYY-MM-DD' limita a un vencimiento (0DTE = hoy). None = default de Schwab.
    """
    if not getattr(sch, "available", False):
        return {"error": "Schwab no disponible — renueva la autorización"}
    spot = sch.last_price(symbol if symbol.startswith("$") else "$" + symbol)
    if not spot:
        return {"error": "sin precio spot de Schwab"}
    chain = sch.chains(symbol, from_date=fecha, to_date=fecha,
                       strike_count=strike_count)
    if not chain:
        return {"error": "Schwab no devolvió la cadena de opciones"}
    r = mvc(chain, spot)
    r["symbol"] = symbol
    r["fecha"] = fecha
    return r
