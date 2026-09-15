#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LENTE VWAP + bandas DS1/DS2 para SPX (método de Nancy: VWAP + reversión + DS1).

Nancy: cuerpo del fly = VWAP (la media a donde revierte); entrada LEJOS = banda DS1
(±1σ). Este lente computa el VWAP intradía y las bandas DS1 (±1σ) y DS2 (±2σ) en
términos de SPX.

Cómo: SPX (índice) no tiene volumen, así que se computa el VWAP sobre SPY (volumen
real, barras 1-min RTH de hoy) y se convierte a SPX con el ratio vivo SPX/SPY.

  vwap_ds_spx() -> dict {vwap, ds1_lo, ds1_hi, ds2_lo, ds2_hi, sd, ratio, ...}

Solo lectura (Schwab price_history). En vivo durante la sesión trae las barras de hoy.
Post-cierre el historial puede ir con lag (usa el último día disponible y lo avisa).
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, date

sys.path.insert(0, r"C:\Users\tania\Desktop\warren-buffett-jr\engine")
from wbj.config import load_settings                # noqa: E402
from wbj.providers.schwab import SchwabProvider     # noqa: E402


def _sch():
    s = load_settings()
    return SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                          s.schwab_callback_url, s.schwab_token_path)


def vwap_ds_spx(sch=None, proxy="SPY"):
    sch = sch or _sch()
    # Barras de HOY: rango explicito (con period=N Schwab solo da dias CERRADOS).
    now = datetime.now()
    start_ms = int(datetime.combine(now.date(), datetime.min.time()).timestamp() * 1000)
    end_ms = int(now.timestamp() * 1000)
    bars = sch.price_history(proxy, period_type="day", frequency_type="minute",
                             frequency=1, start_date=start_ms, end_date=end_ms)
    # Fallback: pre-market/fin de semana sin barras de hoy -> ultimos 2 dias cerrados.
    if not bars:
        bars = sch.price_history(proxy, period_type="day", period=2,
                                 frequency_type="minute", frequency=1)
    if not bars:
        return None
    # dia mas reciente disponible, solo RTH (9:30-16:00 local = ET)
    def d(x): return datetime.fromtimestamp(x["datetime"] / 1000)
    ultimo = max(d(x).date() for x in bars)
    rows = [x for x in bars if d(x).date() == ultimo and 9 <= d(x).hour < 16
            and not (d(x).hour == 9 and d(x).minute < 30)]
    if not rows:
        return None
    num = den = 0.0
    tps = []
    for x in rows:
        tp = (x["high"] + x["low"] + x["close"]) / 3
        v = x.get("volume", 0) or 0
        num += tp * v
        den += v
        tps.append((tp, v))
    if not den:
        return None
    vwap = num / den
    sd = math.sqrt(sum(v * (tp - vwap) ** 2 for tp, v in tps) / den)
    # ratio SPX/SPY vivo (o cierre de la barra si el indice no cotiza)
    spx_last = sch.last_price("$SPX")
    proxy_last = sch.last_price(proxy) or rows[-1]["close"]
    ratio = (spx_last / proxy_last) if (spx_last and proxy_last) else 9.97
    R = lambda p: round(p * ratio, 1)
    return {
        "fecha_barras": str(ultimo), "es_hoy": ultimo == date.today(),
        "vwap": R(vwap), "sd_spx": round(sd * ratio, 1),
        "ds1_lo": R(vwap - sd), "ds1_hi": R(vwap + sd),
        "ds2_lo": R(vwap - 2 * sd), "ds2_hi": R(vwap + 2 * sd),
        "ratio": round(ratio, 3), "spx_last": spx_last,
    }


def main() -> int:
    r = vwap_ds_spx()
    if not r:
        print("Sin datos de barras."); return 1
    lag = "" if r["es_hoy"] else f"  [OJO barras de {r['fecha_barras']}, lag post-cierre]"
    print(f"VWAP SPX {r['vwap']} | DS1 [{r['ds1_lo']}, {r['ds1_hi']}] "
          f"| DS2 [{r['ds2_lo']}, {r['ds2_hi']}] | 1sd {r['sd_spx']}pt{lag}")
    print(f"  (spot {r['spx_last']} | ratio {r['ratio']})")
    print("  Nancy: cuerpo de fly = VWAP; entrar en DS1 (lejos=prima); reversion al VWAP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
