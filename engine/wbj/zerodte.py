"""Ruta de entrada 0DTE — sistema SEPARADO de la confluencia de 3 lentes.

NO mezclar con `confluencia.py` (esa es la ruta SWING / no-0DTE con las 3 lentes).
Corroborado con las clases de Tania (Escuela/):

- *Gamma, Charm y lectura de MM en 0DTE*: se lee gamma (contiene/acelera), charm
  (el reloj) y straddle (Spot vs Straddle). "En 0DTE, dirección no es suficiente;
  el movimiento tiene que ganarle al tiempo."
- *El Poder de Vanna*: el vol crush (el VIX cae 2-4 pts en minutos) = viento de cola,
  terreno del vendedor de prima. En 0DTE el crush marca la **SALIDA** (toma de
  ganancia en la mariposa / el movimiento se agotó), NO la entrada.

REGLAS (v0 — se irá mejorando conforme Tania y Claude aprenden):
- **Volumen OBLIGATORIO** (como toda entrada de Tania; se mide con Schwab/SPY).
- **ENTRADA 0DTE:** volumen + lectura de dealer (SPX sobre el Gamma Flip = modo imán,
  y el spot yendo al imán = "cuando va a subir"). **No** se usan las 3 confluencias.
- **CRUSH del VIX = SALIDA**, no entrada: cuando el VIX/straddle rueda desde el pico,
  es hora de cerrar.

El precio, el VIX y el volumen se sacan solos de Schwab. La lectura de dealer
(Gamma Flip, dirección del spot al imán) hoy la aporta Tania desde VS3D; mejora
futura: derivarla de la cadena de Schwab.
"""
from __future__ import annotations


def tendencia_vix(q: dict | None) -> dict:
    """Deriva la tendencia intradía del VIX del quote de Schwab (máx/mín/último del día).

    Sin historial intradía, usa dónde está el VIX dentro del rango del día:
    - 'subiendo' = pegado al máximo (pico vivo)
    - 'girando'  = empezó a bajar del máximo (el crush puede estar cerca)
    - 'bajando'  = claramente rodando desde el máximo (CRUSH en curso)
    - None       = sin datos suficientes
    """
    if not isinstance(q, dict):
        return {"tendencia": None, "razon": "sin quote del VIX"}
    hi, lo, last = q.get("highPrice"), q.get("lowPrice"), q.get("lastPrice")
    if not all(isinstance(x, (int, float)) for x in (hi, lo, last)) or hi <= lo:
        return {"tendencia": None, "razon": "quote del VIX sin máx/mín/último válidos"}
    retroceso = (hi - last) / (hi - lo)     # 0 = en el máximo, 1 = en el mínimo
    t = "subiendo" if retroceso <= 0.15 else "bajando" if retroceso >= 0.40 else "girando"
    return {"tendencia": t, "retroceso": round(retroceso, 2),
            "high": hi, "low": lo, "last": last, "open": q.get("openPrice"),
            "razon": (f"VIX {last:.2f} · día [{lo:.2f}-{hi:.2f}] · "
                      f"retrocedió {retroceso*100:.0f}% desde el máx -> {t}")}


def estado_vix_0dte(vix_nivel: float | None,
                    vix_tendencia: str | None = None) -> dict:
    """Régimen del VIX para 0DTE. En 0DTE el crush es señal de SALIDA.

    `vix_tendencia`: 'subiendo' (pico vivo) · 'girando' (empieza a rodar, vigilar
    salida) · 'bajando' (CRUSH -> SALIDA) · None (no disponible).
    """
    n = f"{vix_nivel:.2f}" if isinstance(vix_nivel, (int, float)) else "?"
    if vix_tendencia == "bajando":
        return {"crush": True, "girando": False,
                "razon": f"VIX bajando desde el pico ({n}) = CRUSH en curso -> SALIDA"}
    if vix_tendencia == "girando":
        return {"crush": False, "girando": True,
                "razon": f"VIX ({n}) empieza a rodar desde el máx del día -> vigilar SALIDA (crush cerca)"}
    if vix_tendencia == "subiendo":
        return {"crush": False, "girando": False,
                "razon": f"VIX subiendo ({n}) = pico vivo, el crush aún no llega"}
    return {"crush": False, "girando": False,
            "razon": f"VIX {n} — tendencia intradía no disponible"}


def franja_intradia(ahora_et=None) -> dict:
    """Reloj intradía para 0DTE (clase Latino Wall Street 2026-07-27):

    - mañana (apertura–11 ET): manda VANNA / picos de vol -> NO entrar mariposa.
    - 11–13 ET: VENTANA de mariposa (manda theta, menos movimientos bruscos).
    - después de 13 ET: el CHARM activa el GAMMA -> movimientos erráticos.
    """
    from datetime import datetime
    if ahora_et is None:
        try:
            from zoneinfo import ZoneInfo
            ahora_et = datetime.now(ZoneInfo("America/New_York"))
        except Exception:  # noqa: BLE001
            return {"franja": None, "hora_et": None, "mariposa_favorable": None,
                    "nota": "no pude determinar la hora ET"}
    h = ahora_et.hour + ahora_et.minute / 60.0
    hhmm = ahora_et.strftime("%H:%M")
    if h < 11:
        return {"franja": "mañana", "hora_et": hhmm, "mariposa_favorable": False,
                "nota": "mañana: manda Vanna / picos de vol -> esperar la ventana 11-13 ET"}
    if h < 13:
        return {"franja": "ventana_mariposa", "hora_et": hhmm, "mariposa_favorable": True,
                "nota": "11-13 ET: ventana de mariposa (theta manda, menos movimientos bruscos)"}
    return {"franja": "tarde", "hora_et": hhmm, "mariposa_favorable": False,
            "nota": "tarde: el charm activa el gamma (errático) -> cuidado con la mariposa"}


def ruta_0dte(symbol: str = "$SPX", *, iman: float | None = None,
              gamma_flip: float | None = None,
              call_wall: float | None = None,
              put_wall: float | None = None,
              sobre_gamma_flip: bool | None = None,
              spot_va_a_subir: bool | None = None,
              vix_tendencia: str | None = None) -> dict:
    """Valida una entrada 0DTE con volumen + dealer; el crush del VIX es SALIDA.

    Automático (Schwab): precio, VIX (nivel + tendencia), volumen.
    Aportado por Tania desde VS3D (la clase 'La Curva del SPX' dice que los niveles
    del dealer salen de la herramienta, NO se calculan a mano): `iman`, `gamma_flip`,
    `call_wall`, `put_wall`. Con `gamma_flip` numérico, `sobre_gamma_flip` se deriva
    solo (precio vs flip). `spot_va_a_subir` es la dirección al imán (lo lee Tania).
    """
    from wbj.config import load_settings
    from wbj.providers.schwab import SchwabProvider
    from wbj.volumen import volumen_estado

    s = load_settings()
    sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                         s.schwab_callback_url, s.schwab_token_path,
                         history_dir=s.history_dir)
    disp = getattr(sch, "available", False)
    sym = symbol if symbol.startswith("$") else "$" + symbol
    q = sch.quote(sym) if disp else None
    precio = float(q["lastPrice"]) if q and q.get("lastPrice") else None
    vix_q = sch.quote("$VIX") if disp else None
    vix = float(vix_q["lastPrice"]) if vix_q and vix_q.get("lastPrice") else None

    vol = volumen_estado(symbol, sch) if disp else {"error": "Schwab no disponible"}
    volumen_ok = bool(vol.get("elevado"))

    # Auto-detección de la tendencia del VIX (si Tania no la aportó a mano).
    tv = tendencia_vix(vix_q)
    if vix_tendencia is None:
        vix_tendencia = tv.get("tendencia")
    vixs = estado_vix_0dte(vix, vix_tendencia)
    vixs["auto"] = tv
    crush = vixs["crush"]

    # Si Tania dio el NIVEL del Gamma Flip (de VS3D), derivo 'sobre_gamma_flip' solo.
    flip_auto = None
    if sobre_gamma_flip is None and gamma_flip is not None and precio is not None:
        sobre_gamma_flip = precio > gamma_flip
        flip_auto = (f"precio {precio:.2f} {'>' if sobre_gamma_flip else '<='} "
                     f"gamma_flip {gamma_flip:.2f}")

    # Estimación GEX de Schwab (una sola bajada de cadena): sirve de fallback para el
    # régimen de gamma Y la dirección al imán. VS3D siempre manda si Tania lo aporta.
    from wbj.gamma_flip import gamma_flip_estimado
    gex_est = gamma_flip_estimado(symbol)
    gex_ok = not gex_est.get("error")

    # 1) Régimen de gamma (¿sobre el flip?).
    if sobre_gamma_flip is not None:
        fuente_gamma = "VS3D (Tania)"
    elif gex_ok:
        sobre_gamma_flip = gex_est.get("sobre_flip_est")
        fuente_gamma = "estimación Schwab GEX (CONFIRMAR con VS3D)"
    else:
        fuente_gamma = "ninguna"

    # 2) Dirección al imán ("va a subir"). Solo es fiable SOBRE el flip (hay pin);
    #    bajo el flip no hay pin fiable (La Curva del SPX) -> no se marca subir.
    if spot_va_a_subir is not None:
        fuente_dir = "VS3D (Tania)"
    elif gex_ok:
        pin_fiable = bool(gex_est.get("sobre_flip_est"))
        spot_va_a_subir = (gex_est.get("direccion_est") == "subir") if pin_fiable else False
        fuente_dir = (f"estimación GEX (imán {gex_est.get('iman_est')}, "
                      f"{'pin fiable sobre el flip' if pin_fiable else 'sin pin bajo el flip'})")
    else:
        fuente_dir = "ninguna"

    # Lectura de dealer (régimen + dirección; VS3D lo confirma).
    dealer_ok = bool(sobre_gamma_flip) and bool(spot_va_a_subir)

    faltan: list[str] = []
    if not volumen_ok:
        faltan.append("VOLUMEN (no elevado)")
    if sobre_gamma_flip is None or spot_va_a_subir is None:
        faltan.append("lectura de dealer/VS3D (Gamma Flip + dirección al imán) — la aporta Tania")
    else:
        if not sobre_gamma_flip:
            faltan.append("SPX NO está sobre el Gamma Flip (no es modo imán)")
        if not spot_va_a_subir:
            faltan.append("el spot no va hacia el imán ('cuando va a subir')")

    # Confluencias para la MARIPOSA 0DTE (checklist; incluye gamma=velocidad del video
    # VolSignals + el reloj intradía + el régimen + volumen). VS3D confirma.
    franja = franja_intradia()
    gl = (gex_est or {}).get("gamma_local") or {} if gex_ok else {}
    conf_mariposa = {
        "sobre_flip": sobre_gamma_flip,
        "gamma_pesada": (gl.get("densidad") == "pesada") if gl else None,
        "ventana_11_13": franja.get("mariposa_favorable"),
        "vix_no_picando": (vix_tendencia != "subiendo"),
        "volumen": volumen_ok,
        "direccion_al_iman": bool(spot_va_a_subir) if spot_va_a_subir is not None else None,
    }
    conf_mariposa["cuantas_ok"] = sum(1 for k, v in conf_mariposa.items() if v is True)

    if crush:
        tipo, veredicto = "salida", (
            "SALIDA (CRUSH): el VIX rueda desde el pico -> toma de ganancia / cerrar. "
            "En 0DTE el crush NO es entrada.")
    elif volumen_ok and dealer_ok:
        tipo, veredicto = "entrada", (
            "POSIBLE ENTRADA 0DTE: volumen + dealer OK y el crush aún no llegó. "
            "Recordatorio: el crush será tu SALIDA.")
    else:
        tipo = "vigilar"
        veredicto = "VIGILAR — falta: " + ", ".join(faltan) if faltan else "VIGILAR"

    return {
        "sistema": "0DTE (volumen + dealer; crush = SALIDA) — NO usa las 3 confluencias",
        "precio": precio, "vix": vix, "iman": iman,
        "volumen": vol, "volumen_ok": volumen_ok,
        "dealer": {"sobre_gamma_flip": sobre_gamma_flip, "flip_auto": flip_auto,
                   "gamma_flip": gamma_flip, "call_wall": call_wall,
                   "put_wall": put_wall, "spot_va_a_subir": spot_va_a_subir,
                   "ok": dealer_ok, "fuente_gamma": fuente_gamma,
                   "fuente_dir": fuente_dir, "gex_estimado": gex_est},
        "vix_estado": vixs,
        "ventana_intradia": franja,
        "confluencia_mariposa": conf_mariposa,
        "modo_operativo": (gex_est or {}).get("modo_operativo") if gex_ok else None,
        "tipo_senal": tipo,
        "veredicto": veredicto,
        "regla": ("0DTE: volumen OBLIGATORIO + lectura de dealer (gamma/charm/straddle) "
                  "para entrar 'cuando va a subir'; el CRUSH del VIX es la SALIDA. "
                  "NO se usan las 3 confluencias (eso es swing). Corroborado con las clases."),
        "nota_v0": ("v0 — mejorar: auto-detectar la tendencia del VIX y el Gamma Flip "
                    "desde la cadena de Schwab. Hoy el dealer read lo aporta Tania por VS3D."),
    }
