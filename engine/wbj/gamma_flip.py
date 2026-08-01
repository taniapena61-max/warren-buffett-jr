"""Estimación del Gamma Flip / muros / régimen desde la cadena de Schwab (GEX).

⚠️ IMPORTANTE (corroborado con la clase 'La Curva del SPX'): el Gamma Flip REAL sale
de la herramienta (VS3D/VolSignals). Esto es una **ESTIMACIÓN secundaria** para
corroborar y afinar hacia la independencia futura — **NUNCA sustituye a VS3D**.

Modelo (convención naive de dealer, estilo SpotGamma):
- Dealer LARGO de gamma en calls, CORTO en puts. Signo + calls / − puts.
- GEX(S) por opción = gamma(S) · OI · 100 · S² · 0.01.
- **Régimen** (fiable): signo del GEX neto al spot actual. < 0 = corto gamma /
  amplifica / nervioso (BAJO el flip); > 0 = largo gamma / contiene / tranquilo.
- **Gamma Flip** (estimado): se re-valúa la gamma de cada opción con Black-Scholes
  (IV, tiempo a vencimiento y tasa de la cadena) sobre una malla de spots, y se busca
  el spot donde el GEX neto cruza cero. Aproximado; se compara con VS3D para afinar.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone


def _filas_cadena(ch: dict) -> tuple[list[dict], str | None]:
    """Aplana la cadena a filas {strike, gamma, oi, vol, iv, tipo} + fecha de vto ISO."""
    filas: list[dict] = []
    exp_iso: str | None = None
    for lado, tipo in (("callExpDateMap", "call"), ("putExpDateMap", "put")):
        for _exp, strikes in (ch.get(lado) or {}).items():
            for k, lst in strikes.items():
                o = lst[0] if lst else None
                if not isinstance(o, dict):
                    continue
                g, oi, iv = o.get("gamma"), o.get("openInterest"), o.get("volatility")
                if not isinstance(g, (int, float)) or not isinstance(oi, (int, float)):
                    continue
                if exp_iso is None:
                    exp_iso = o.get("expirationDate")
                d = o.get("delta")
                filas.append({
                    "strike": float(o.get("strikePrice", k)), "gamma": float(g),
                    "oi": int(oi), "vol": int(o.get("totalVolume") or 0),
                    "iv": (float(iv) / 100.0 if isinstance(iv, (int, float)) and iv > 0 else None),
                    "delta": float(d) if isinstance(d, (int, float)) else None,
                    "tipo": tipo})
    return filas, exp_iso


def rango_por_delta(filas: list[dict], targets=(0.20, 0.25, 0.30)) -> dict:
    """Strikes por delta desde la cadena (call y put). El .25 ≈ rango esperado / alas.

    Lo que Tania llama 'deltas de apertura' — antes se olvidaba buscarlos en la cadena.
    """
    calls = [f for f in filas if f["tipo"] == "call" and isinstance(f.get("delta"), (int, float))]
    puts = [f for f in filas if f["tipo"] == "put" and isinstance(f.get("delta"), (int, float))]
    out: dict = {}
    for t in targets:
        c = min(calls, key=lambda f: abs(f["delta"] - t), default=None)
        p = min(puts, key=lambda f: abs(abs(f["delta"]) - t), default=None)
        k = int(t * 100)
        out[f"call_{k}"] = {"strike": c["strike"], "delta": round(c["delta"], 3)} if c else None
        out[f"put_{k}"] = {"strike": p["strike"], "delta": round(p["delta"], 3)} if p else None
    return out


def _bs_gamma(S: float, K: float, T: float, r: float, sig: float) -> float:
    """Gamma Black-Scholes de una opción (calls y puts comparten gamma)."""
    if S <= 0 or K <= 0 or T <= 0 or sig <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sig * sig) * T) / (sig * math.sqrt(T))
    pdf = math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
    return pdf / (S * sig * math.sqrt(T))


def _net_gex_en(filas: list[dict], S: float, T: float | None, r: float) -> float:
    """GEX neto del dealer al spot S (BS si hay IV+T; si no, la gamma reportada)."""
    tot = 0.0
    for f in filas:
        if f["iv"] is not None and T:
            g = _bs_gamma(S, f["strike"], T, r, f["iv"])
        else:
            g = f["gamma"]  # fallback: solo válida en el spot actual
        signo = 1.0 if f["tipo"] == "call" else -1.0
        tot += signo * g * f["oi"] * 100 * S * S * 0.01
    return tot


def _flip_bs(filas: list[dict], spot: float, T: float, r: float,
             rango: float = 0.05, paso: float = 2.0) -> float | None:
    """Busca el spot donde el GEX neto cruza cero (± `rango` alrededor del spot)."""
    S = spot * (1 - rango)
    hi = spot * (1 + rango)
    prev_S = prev = None
    while S <= hi:
        val = _net_gex_en(filas, S, T, r)
        if prev is not None and ((prev < 0 <= val) or (prev > 0 >= val)):
            return round(prev_S + (S - prev_S) * (0 - prev) / (val - prev), 2)
        prev_S, prev = S, val
        S += paso
    return None


def gamma_flip_estimado(symbol: str = "$SPX", fecha: str | None = None,
                        gamma_flip_vs3d: float | None = None) -> dict:
    """Estima régimen + Gamma Flip (BS) + muros de la cadena 0DTE. Compara con VS3D."""
    from datetime import date as _date
    from wbj.config import load_settings
    from wbj.providers.schwab import SchwabProvider

    s = load_settings()
    sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                         s.schwab_callback_url, s.schwab_token_path,
                         history_dir=s.history_dir)
    dia = fecha or _date.today().isoformat()
    ch = sch.chains(symbol, from_date=dia, to_date=dia, strike_count=80)
    if not ch or ch.get("status") != "SUCCESS":
        return {"error": "sin cadena de Schwab (¿token vencido?)"}
    spot = ch.get("underlyingPrice")
    filas, exp_iso = _filas_cadena(ch)
    if not filas or not isinstance(spot, (int, float)):
        return {"error": "cadena vacía o sin subyacente"}
    spot = float(spot)

    # Tiempo a vencimiento (años) y tasa.
    T = None
    if exp_iso:
        try:
            exp = datetime.fromisoformat(exp_iso)
            seg = (exp - datetime.now(timezone.utc)).total_seconds()
            T = seg / (365 * 24 * 3600) if seg > 0 else None
        except (ValueError, TypeError):
            T = None
    r_tasa = float(ch.get("interestRate") or 0) / 100.0

    net_gex = _net_gex_en(filas, spot, T, r_tasa)
    flip = _flip_bs(filas, spot, T, r_tasa) if T else None
    regimen = ("largo gamma: contiene / tranquilo (SOBRE el flip)" if net_gex > 0
               else "corto gamma: amplifica / nervioso (BAJO el flip)")

    calls = [f for f in filas if f["tipo"] == "call" and f["strike"] >= spot]
    puts = [f for f in filas if f["tipo"] == "put" and f["strike"] <= spot]
    call_wall = max(calls, key=lambda f: f["oi"])["strike"] if calls else None
    put_wall = max(puts, key=lambda f: f["oi"])["strike"] if puts else None

    # Imán / pin = pico de la campana = strike con más concentración de gamma (gamma·OI).
    # (La Curva del SPX: el precio se pega al pico SOLO sobre el flip; abajo no pinea.)
    conc: dict[float, float] = defaultdict(float)
    for f in filas:
        conc[f["strike"]] += f["gamma"] * f["oi"]
    iman_est = max(conc, key=conc.get) if conc else None
    if iman_est is None:
        direccion_est = None
    elif iman_est > spot + 2:
        direccion_est = "subir"
    elif iman_est < spot - 2:
        direccion_est = "bajar"
    else:
        direccion_est = "en el imán"

    # Densidad de gamma LOCAL alrededor del spot (video VolSignals: gamma = VELOCIDAD;
    # pesada -> mercado lento / pin (favorece mariposa); fina -> vacío / momentum (evitar).
    # Proxy: concentración media (gamma·OI) en ±15 pts vs el pico (imán).
    banda = [conc[k] for k in conc if abs(k - spot) <= 15]
    pico = conc.get(iman_est, 0) if iman_est is not None else 0
    local = (sum(banda) / len(banda)) if banda else 0
    ratio = round(local / pico, 2) if pico else 0.0
    densidad = "pesada" if ratio >= 0.5 else ("fina" if ratio < 0.2 else "media")
    gamma_local = {"densidad": densidad, "ratio_vs_pico": ratio,
                   "nota": {"pesada": "gamma pesada -> mercado lento / pin (favorece mariposa)",
                            "media": "gamma media",
                            "fina": "gamma fina -> vacío / momentum (evitar mariposa)"}[densidad]}

    # Modo operativo según el signo de la gamma (video VolSignals "gamma profile"):
    # VERDE (gamma+) = estable -> VENDER PRIMA; ROJO (gamma-) = errático -> COMPRAR opciones.
    modo_operativo = (
        "gamma+ (VERDE/estable): VENDER PRIMA (mariposa/verticales); fade extensiones"
        if net_gex > 0 else
        "gamma- (ROJO/errático): COMPRAR opciones / momentum; NO vender prima "
        "(el movimiento no para hasta llegar a gamma+)")

    r = {"fuente": "GEX estimado (Schwab, BS) — ESTIMACIÓN, no sustituye a VS3D",
         "spot": round(spot, 2), "gamma_flip_est": flip,
         "regimen_gamma": regimen, "net_gex_B": round(net_gex / 1e9, 2),
         "sobre_flip_est": net_gex > 0,
         "call_wall_est": call_wall, "put_wall_est": put_wall,
         "iman_est": iman_est, "direccion_est": direccion_est,
         "gamma_local": gamma_local, "modo_operativo": modo_operativo,
         "rango_delta": rango_por_delta(filas),
         "horas_a_vto": round(T * 365 * 24, 2) if T else None,
         "n_strikes": len({f["strike"] for f in filas}), "fecha": dia}

    if gamma_flip_vs3d is not None and flip is not None:
        dif = round(flip - gamma_flip_vs3d, 2)
        r["vs3d"] = {"gamma_flip_vs3d": gamma_flip_vs3d, "diferencia": dif,
                     "coincide_10pts": abs(dif) <= 10}
    return r
