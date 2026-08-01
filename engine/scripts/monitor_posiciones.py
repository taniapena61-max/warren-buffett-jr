"""Monitor de posiciones de Tania — opciones largas, puts vendidos y acciones.

Lee `API/posiciones.json`, consulta Schwab en vivo y decide si hay algo que
avisar. Cada tipo de posicion tiene su propio riesgo, asi que sus disparadores
son distintos:

  opcion_larga (sus LEAPs de PLTR)
      ALERTA al +25% sobre el costo, IDEAL al +50%. Gana si la opcion sube.

  opcion_corta (sus puts VENDIDOS de IREN)
      Gana si la opcion BAJA. Lo que la amenaza es la asignacion, asi que
      vigila tres cosas distintas:
        - ASIGNACION TEMPRANA: el valor temporal casi agotado es lo que de
          verdad provoca que ejerzan contra ella (no el simple estar ITM).
        - PROFUNDIDAD ITM: cuanto por debajo del strike esta la accion.
        - GANANCIA CAPTURADA: % de la prima ya ganado, por si quiere cerrar.

  accion
      P/L contra el costo y ruptura de niveles criticos declarados.

Salida: texto para el chat y email por Resend cuando algo dispara. Nunca
ejecuta ordenes: informa, Tania decide y opera en su broker.

Uso:
    python scripts/monitor_posiciones.py            # revisa y avisa si dispara
    python scripts/monitor_posiciones.py --forzar   # reporta y envia siempre
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from html import escape as _esc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wbj.config import load_settings  # noqa: E402
from wbj.providers.schwab import SchwabProvider  # noqa: E402
from wbj.providers.tradestation import TradeStationProvider  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
POSICIONES = REPO / "API" / "posiciones.json"
ESTADO = REPO / "API" / "monitor_estado.json"


def _cargar(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return default


def _quote(sch, simbolo, intentos: int = 3):
    """Cotizacion con reintentos.

    Schwab falla de forma intermitente cuando se le piden varios simbolos
    seguidos. Sin reintento, una posicion quedaria sin vigilar EN SILENCIO
    justo el dia que importa, asi que se insiste antes de darla por perdida.
    """
    import time
    for i in range(intentos):
        try:
            q = sch.quote(simbolo)
            if q and (q.get("mark") is not None or q.get("lastPrice") is not None):
                return q
        except Exception:  # noqa: BLE001 — una falla no debe tumbar el resto
            pass
        if i < intentos - 1:
            time.sleep(1.5)
    return None


def _num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _dias_a_vencimiento(iso: str | None) -> int | None:
    """Días desde hoy hasta la fecha de vencimiento ISO de TS, o None."""
    if not iso:
        return None
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (d - datetime.now(timezone.utc)).days
    except ValueError:
        return None


def revisar_tradestation(cfg: dict, previo_ts: dict) -> tuple[list, list, dict]:
    """Watchdog del portafolio de TradeStation (TS). Vigila SOLO las OPCIONES que
    Tania pidió: LEAPs (vencen a más de `ts_dias_leap`) y las que vencen pronto
    (en `ts_dias_corto` días o menos). NO vigila acciones ni las opciones del rango
    intermedio. Avisa cuando una posición vigilada mueve su P/L >= `ts_movimiento_usd`
    desde la última revisión. Si TS no está conectado, devuelve vacío (no rompe)."""
    s = load_settings()
    ts = TradeStationProvider(s.tradestation_client_id, s.tradestation_client_secret,
                              s.tradestation_callback_url, s.tradestation_token_path)
    if not ts.available:
        return [], [], previo_ts
    acc = ts.accounts()
    ids = [a.get("AccountID") for a in (acc or {}).get("Accounts", [])]
    if not ids:
        return [], [], previo_ts
    pos = ts.positions(",".join(ids))
    plist = (pos or {}).get("Positions") or []
    if not plist:
        return [], [], previo_ts

    umbral = cfg.get("ts_movimiento_usd", 300)  # $ de cambio de P/L que dispara
    dias_corto = cfg.get("ts_dias_corto", 183)  # frontera "<6 meses" (para etiqueta)
    disparos, estado, movers = [], {}, 0
    tot_mv = tot_pl = 0.0
    n_vig = 0
    for p in plist:
        if "OPTION" not in str(p.get("AssetType", "")).upper():
            continue  # solo OPCIONES (LEAPs y cortas); las acciones NO se vigilan
        dias = _dias_a_vencimiento(p.get("ExpirationDate"))
        sym = p.get("Symbol")
        pl = _num(p.get("UnrealizedProfitLoss"))
        tot_mv += _num(p.get("MarketValue"))
        tot_pl += pl
        n_vig += 1
        estado[sym] = round(pl, 2)
        antes = previo_ts.get(sym)
        if antes is not None and abs(pl - antes) >= umbral:
            movers += 1
            etq = "LEAP" if (dias or 0) > dias_corto else f"vence en {dias}d"
            disparos.append(
                f"TS MOVIMIENTO: {sym} ({etq}) P/L ${antes:+,.0f} -> ${pl:+,.0f} "
                f"(cambio ${pl - antes:+,.0f})")
    fila = {"tipo": "ts_resumen",
            "desc": f"TradeStation — {n_vig} opciones vigiladas (sin acciones)",
            "mv": round(tot_mv, 0), "pl": round(tot_pl, 0),
            "movers": movers, "umbral": umbral}
    return [fila], disparos, estado


def revisar() -> dict:
    cfg = _cargar(POSICIONES, {})
    if not cfg.get("posiciones"):
        return {"error": "no hay posiciones configuradas en API/posiciones.json"}

    s = load_settings()
    sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                         s.schwab_callback_url, s.schwab_token_path,
                         history_dir=s.history_dir)  # archiva cada consulta
    if not sch.available:
        return {"error": "Schwab no autorizado — renueva con 'Renovar Schwab.bat'"}

    previo = _cargar(ESTADO, {})
    alerta_pct = cfg.get("alerta_pct", 25)
    ideal_pct = cfg.get("ideal_pct", 50)
    mov_pct = cfg.get("movimiento_importante_pct", 8)
    vt_critico = cfg.get("valor_temporal_critico", 0.50)

    filas, disparos, nuevo = [], [], {}
    for p in cfg["posiciones"]:
        tipo = p.get("tipo", "opcion_larga")
        q = _quote(sch, p["simbolo_schwab"])
        if not q:
            filas.append({"id": p["id"], "desc": p["descripcion"],
                          "error": "sin cotizacion"})
            continue

        # ---------------------------------------------------------- indice
        # Solo vigila cruces de nivel (no es una posicion, no hay P/L).
        if tipo == "indice":
            px = q.get("lastPrice") or q.get("mark")
            if px is None:
                filas.append({"id": p["id"], "desc": p["descripcion"],
                              "error": "sin precio"})
                continue
            px = float(px)
            # Etiqueta del subyacente para la alerta (antes fijo en "SPX", roto
            # cuando se vigila otro simbolo como META). Cae al simbolo si falta.
            etq = p.get("etiqueta") or p.get("simbolo_schwab", "nivel").lstrip("$")
            antes = previo.get(p["id"], {}).get("precio")
            niveles = p.get("niveles_etiquetados", [])
            for nv in niveles:
                lv, sentido = float(nv["precio"]), nv.get("sentido", "abajo")
                if antes is None:
                    continue
                af = float(antes)
                if sentido == "abajo" and af >= lv > px:
                    disparos.append(f"{etq} rompio ${lv:g} a la BAJA: {nv['que']} "
                                    f"— ahora {px:.2f}")
                elif sentido == "arriba" and af <= lv < px:
                    disparos.append(f"{etq} alcanzo ${lv:g}: {nv['que']} "
                                    f"— ahora {px:.2f}")
            nuevo[p["id"]] = {"precio": px, "visto": datetime.now().isoformat()}
            filas.append({"id": p["id"], "desc": p["descripcion"], "tipo": "indice",
                          "precio": round(px, 2), "niveles": niveles})
            continue

        # ---------------------------------------------------------- acciones
        if tipo == "accion":
            px = q.get("lastPrice") or q.get("mark")
            if px is None:
                filas.append({"id": p["id"], "desc": p["descripcion"],
                              "error": "sin precio"})
                continue
            px = float(px)
            costo = float(p["costo_por_accion"])
            n = int(p.get("acciones", 0))
            pl_pct = (px / costo - 1) * 100
            fila = {"id": p["id"], "desc": p["descripcion"], "tipo": tipo,
                    "precio": round(px, 2), "costo": costo,
                    "pl_pct": round(pl_pct, 1),
                    "pl_usd": round((px - costo) * n, 0)}
            # Niveles etiquetados: avisan al CRUZAR, y dicen que significan.
            # "abajo" = riesgo al perderlo; "arriba" = oportunidad al alcanzarlo.
            antes = previo.get(p["id"], {}).get("precio")
            niveles = p.get("niveles_etiquetados", [])
            for nv in niveles:
                lv, sentido = float(nv["precio"]), nv.get("sentido", "abajo")
                if antes is None:
                    continue
                antes_f = float(antes)
                if sentido == "abajo" and antes_f >= lv > px:
                    disparos.append(f"NIVEL PERDIDO ${lv:.2f}: {nv['que']} "
                                    f"— IREN cayo a ${px:.2f}")
                elif sentido == "arriba" and antes_f <= lv < px:
                    disparos.append(f"NIVEL ALCANZADO ${lv:.2f}: {nv['que']} "
                                    f"— IREN subio a ${px:.2f}")
            fila["niveles"] = niveles
            nuevo[p["id"]] = {"precio": px, "visto": datetime.now().isoformat()}
            filas.append(fila)
            continue

        # ---------------------------------------------------------- opciones
        mark = q.get("mark")
        if mark is None:
            filas.append({"id": p["id"], "desc": p["descripcion"],
                          "error": "sin cotizacion"})
            continue
        mark = float(mark)
        n = int(p.get("contratos", 1))
        subyacente = q.get("underlyingPrice")
        vt = q.get("timeValue")

        if tipo == "opcion_corta":
            prima = float(p["prima_recibida"])
            strike = float(p.get("strike", 0))
            # vendida: gana lo que la opcion BAJA respecto a la prima cobrada
            ganado_pct = (prima - mark) / prima * 100
            # Valor extrinseco REAL = mark - intrinseco. El campo timeValue de
            # Schwab NO es confiable (reporta ~0 cuando el extrinseco real es
            # >$1), asi que lo calculamos. Es lo que de verdad protege de la
            # asignacion temprana.
            extrinseco = None
            if subyacente is not None:
                intrinseco = max(0.0, strike - float(subyacente))
                extrinseco = round(mark - intrinseco, 2)
            fila = {"id": p["id"], "desc": p["descripcion"], "tipo": tipo,
                    "prima": prima, "mark": round(mark, 2),
                    "ganado_pct": round(ganado_pct, 1),
                    "pl_usd": round((prima - mark) * 100 * n, 0),
                    "strike": strike, "subyacente": subyacente,
                    "valor_temporal": extrinseco,
                    "delta": q.get("delta"),
                    "equilibrio": round(strike - prima, 2)}
            if subyacente is not None:
                fila["itm"] = round(strike - float(subyacente), 2)

            # 1) asignacion temprana: la provoca el extrinseco casi agotado
            #    estando ITM (no los dias que falten). Es una condicion que se
            #    sostiene dias enteros, asi que se avisa UNA vez por dia; sin
            #    esto, un monitor agendado cada pocos minutos manda el mismo
            #    correo sin parar y sepulta lo que si es nuevo.
            if extrinseco is not None and extrinseco < vt_critico and \
                    subyacente is not None and float(subyacente) < strike:
                hoy = datetime.now().strftime("%Y-%m-%d")
                if previo.get(p["id"], {}).get("asignacion_avisada") != hoy:
                    disparos.append(
                        f"RIESGO ASIGNACION TEMPRANA: {p['descripcion']} — valor "
                        f"extrinseco ${extrinseco:.2f} (bajo ${vt_critico:.2f}) e ITM. "
                        f"Pueden ejercerte antes del vencimiento.")
                fila["asignacion_avisada"] = hoy
            # 2) profundidad ITM — solo cuando EMPEORA, no en cada revision.
            # Estar ITM es un estado permanente; avisarlo cada media hora seria
            # ruido y acabaria por enterrar la alerta que si importa. Solo se
            # avisa al cruzar un escalon nuevo de 5 puntos de profundidad.
            if subyacente is not None and float(subyacente) < strike:
                prof = (strike - float(subyacente)) / strike * 100
                fila["itm_pct"] = round(prof, 1)
                escalon = int(prof // 5) * 5
                previo_esc = previo.get(p["id"], {}).get("itm_escalon", 0)
                if prof >= 10 and escalon > previo_esc:
                    disparos.append(
                        f"ITM SE PROFUNDIZA: {p['descripcion']} — "
                        f"{p['simbolo_schwab'][:4]} en ${float(subyacente):.2f}, "
                        f"{prof:.0f}% bajo el strike ${strike:.0f}.")
                fila["itm_escalon"] = escalon
            # 3) ganancia capturada (oportunidad de cerrar barato)
            if ganado_pct >= ideal_pct:
                disparos.append(
                    f"GANANCIA {ganado_pct:.0f}% capturada: {p['descripcion']} "
                    f"— cerrarlo cuesta ${mark:.2f} de los ${prima:.2f} cobrados.")
        else:  # opcion_larga
            costo = float(p["costo_por_accion"])
            pl_pct = (mark / costo - 1) * 100
            fila = {"id": p["id"], "desc": p["descripcion"], "tipo": tipo,
                    "costo": costo, "mark": round(mark, 2),
                    "pl_pct": round(pl_pct, 1),
                    "pl_usd": round((mark - costo) * 100 * n, 0),
                    "objetivo_alerta": round(costo * (1 + alerta_pct / 100), 2),
                    "objetivo_ideal": round(costo * (1 + ideal_pct / 100), 2),
                    "subyacente": subyacente}
            if pl_pct >= ideal_pct:
                disparos.append(f"IDEAL +{ideal_pct}%: {p['descripcion']} en "
                                f"${mark:.2f} ({pl_pct:+.1f}%)")
            elif pl_pct >= alerta_pct:
                disparos.append(f"ALERTA +{alerta_pct}%: {p['descripcion']} en "
                                f"${mark:.2f} ({pl_pct:+.1f}%)")

        antes = previo.get(p["id"], {}).get("mark")
        if antes:
            cambio = (mark / float(antes) - 1) * 100
            fila["cambio"] = round(cambio, 1)
            if abs(cambio) >= mov_pct:
                disparos.append(f"MOVIMIENTO {cambio:+.1f}%: {p['descripcion']} "
                                f"${float(antes):.2f} -> ${mark:.2f}")
        nuevo[p["id"]] = {"mark": mark, "visto": datetime.now().isoformat()}
        if "itm_escalon" in fila:  # recordar el escalon ya avisado
            nuevo[p["id"]]["itm_escalon"] = fila["itm_escalon"]
        if "asignacion_avisada" in fila:  # recordar que ya se aviso hoy
            nuevo[p["id"]]["asignacion_avisada"] = fila["asignacion_avisada"]
        filas.append(fila)

    # --- TradeStation (TS): watchdog de portafolio en vivo ---
    ts_filas, ts_disparos, ts_estado = revisar_tradestation(
        cfg, previo.get("_tradestation", {}))
    filas.extend(ts_filas)
    disparos.extend(ts_disparos)
    nuevo["_tradestation"] = ts_estado

    ESTADO.write_text(json.dumps(nuevo, indent=2), encoding="utf-8")
    return {"hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "filas": filas, "disparos": disparos,
            "email_destino": cfg.get("email_destino")}


def texto(r: dict) -> str:
    if r.get("error"):
        return f"Monitor: {r['error']}"
    out = [f"Monitor de posiciones — {r['hora']}", ""]
    for f in r["filas"]:
        if f.get("error"):
            out.append(f"  {f['desc']}: {f['error']}")
            continue
        t = f.get("tipo")
        if t == "ts_resumen":
            extra = f" · {f['movers']} con movimiento fuerte" if f.get("movers") else ""
            out.append(
                f"  {f['desc']}\n"
                f"    valor ${f['mv']:,.0f} · P/L ${f['pl']:+,.0f}  "
                f"(watchdog: avisa si una posicion mueve >=${f['umbral']:,.0f}){extra}")
            continue
        if t == "indice":
            out.append(
                f"  {f['desc']}: {f['precio']:.2f}\n"
                + "\n".join(f"      ${n['precio']:g} ({n['sentido']}) — {n['que']}"
                            for n in f.get("niveles", [])))
        elif t == "accion":
            out.append(
                f"  {f['desc']}\n"
                f"    costo ${f['costo']:.2f} -> ${f['precio']:.2f}  "
                f"({f['pl_pct']:+.1f}%, ${f['pl_usd']:+,.0f})"
                + ("\n    niveles vigilados:\n" +
                   "\n".join(f"      ${n['precio']:.2f} ({n['sentido']}) — {n['que']}"
                             for n in f["niveles"]) if f.get("niveles") else ""))
        elif t == "opcion_corta":
            sub = f" | IREN ${f['subyacente']:.2f}" if f.get("subyacente") else ""
            itm = (f" | ITM ${f['itm']:.2f}" if f.get("itm", 0) > 0
                   else " | fuera del dinero")
            out.append(
                f"  {f['desc']}  [VENDIDO]\n"
                f"    prima ${f['prima']:.2f} -> cerrar cuesta ${f['mark']:.2f}  "
                f"(ganado {f['ganado_pct']:+.0f}%, ${f['pl_usd']:+,.0f})\n"
                f"    equilibrio ${f['equilibrio']:.2f} | valor temporal "
                f"${f['valor_temporal'] if f['valor_temporal'] is not None else 0:.2f}"
                f"{itm}{sub}")
        else:
            sub = f"  [{f['subyacente']:.2f}]" if f.get("subyacente") else ""
            out.append(
                f"  {f['desc']}\n"
                f"    costo ${f['costo']:.2f} -> mark ${f['mark']:.2f}  "
                f"({f['pl_pct']:+.1f}%, ${f['pl_usd']:+,.0f})\n"
                f"    avisar en ${f['objetivo_alerta']:.2f} · ideal "
                f"${f['objetivo_ideal']:.2f}{sub}")
    out.append("")
    out.append("DISPAROS: " + ("; ".join(r["disparos"]) if r["disparos"] else "ninguno"))
    return "\n".join(out)


# Estilo de celda reutilizable para la tabla del email (los clientes de correo
# ignoran <style>, asi que TODO va inline).
_TD = "style='padding:8px;border-bottom:1px solid #e6e6e6;vertical-align:top'"


def _pl_html(v_pct: float, v_usd: float) -> str:
    """P/L coloreado: verde si gana, rojo si pierde."""
    color = "#0a7d28" if (v_pct or 0) >= 0 else "#b00020"
    return (f"<span style='color:{color};font-weight:bold'>"
            f"{v_pct:+.1f}% (${v_usd:+,.0f})</span>")


def html_reporte(r: dict) -> str:
    """Versión en TABLA del reporte, para el email. Disparos resaltados arriba,
    luego una fila por posición con P/L en color. Todo con estilos inline."""
    if r.get("error"):
        return (f"<div style='font-family:Arial,sans-serif'>"
                f"<p style='color:#b00020'>Monitor: {_esc(r['error'])}</p></div>")

    filas = []
    for f in r["filas"]:
        desc = _esc(f.get("desc", ""))
        if f.get("error"):
            filas.append(f"<tr><td {_TD}>{desc}</td>"
                         f"<td {_TD} colspan='4' style='color:#b00020;padding:8px'>"
                         f"{_esc(f['error'])}</td></tr>")
            continue
        t = f.get("tipo")
        if t == "ts_resumen":
            plc = "#0a7d28" if f.get("pl", 0) >= 0 else "#b00020"
            mov = (f" · <b>{f['movers']}</b> con movimiento fuerte"
                   if f.get("movers") else "")
            filas.append(
                f"<tr><td {_TD}><b>{desc}</b></td>"
                f"<td {_TD}>${f['mv']:,.0f}</td><td {_TD}>—</td>"
                f"<td {_TD}><span style='color:{plc};font-weight:bold'>"
                f"${f['pl']:+,.0f}</span></td>"
                f"<td {_TD} style='padding:8px;font-size:12px;color:#555'>"
                f"watchdog: avisa si una posición mueve ≥${f['umbral']:,.0f}{mov}</td></tr>")
            continue
        if t == "indice":
            niv = "<br>".join(
                f"${n['precio']:g} ({_esc(n['sentido'])}) — {_esc(n['que'])}"
                for n in f.get("niveles", []))
            filas.append(
                f"<tr><td {_TD}>{desc}</td><td {_TD}><b>{f['precio']:.2f}</b></td>"
                f"<td {_TD}>—</td><td {_TD}>—</td>"
                f"<td {_TD} style='padding:8px;font-size:12px;color:#555'>{niv}</td></tr>")
        elif t == "accion":
            niv = "<br>".join(
                f"${n['precio']:.2f} ({_esc(n['sentido'])}) — {_esc(n['que'])}"
                for n in f.get("niveles", []))
            filas.append(
                f"<tr><td {_TD}>{desc}</td><td {_TD}><b>{f['precio']:.2f}</b></td>"
                f"<td {_TD}>${f['costo']:.2f}</td>"
                f"<td {_TD}>{_pl_html(f['pl_pct'], f['pl_usd'])}</td>"
                f"<td {_TD} style='padding:8px;font-size:12px;color:#555'>{niv}</td></tr>")
        elif t == "opcion_corta":
            det = (f"equilibrio ${f['equilibrio']:.2f} · V.temporal "
                   f"${(f['valor_temporal'] or 0):.2f}")
            if f.get("subyacente"):
                det += f" · subyac. ${f['subyacente']:.2f}"
            if f.get("itm", 0) > 0:
                det += f" · ITM ${f['itm']:.2f}"
            filas.append(
                f"<tr><td {_TD}>{desc} <span style='color:#888'>[VENDIDO]</span></td>"
                f"<td {_TD}>cerrar ${f['mark']:.2f}</td>"
                f"<td {_TD}>prima ${f['prima']:.2f}</td>"
                f"<td {_TD}>{_pl_html(f['ganado_pct'], f['pl_usd'])}</td>"
                f"<td {_TD} style='padding:8px;font-size:12px;color:#555'>{det}</td></tr>")
        else:  # opcion_larga
            det = (f"avisar ${f['objetivo_alerta']:.2f} · ideal "
                   f"${f['objetivo_ideal']:.2f}")
            filas.append(
                f"<tr><td {_TD}>{desc}</td><td {_TD}><b>${f['mark']:.2f}</b></td>"
                f"<td {_TD}>${f['costo']:.2f}</td>"
                f"<td {_TD}>{_pl_html(f['pl_pct'], f['pl_usd'])}</td>"
                f"<td {_TD} style='padding:8px;font-size:12px;color:#555'>{det}</td></tr>")

    disparos = r.get("disparos") or []
    if disparos:
        caja = ("<div style='background:#fff3cd;border:1px solid #ffd24d;"
                "border-radius:8px;padding:12px;margin:0 0 16px'>"
                "<div style='font-weight:bold;color:#8a6d00;margin-bottom:6px'>"
                "⚠️ DISPAROS</div><ul style='margin:0;padding-left:20px'>"
                + "".join(f"<li style='margin:4px 0'>{_esc(d)}</li>"
                          for d in disparos) + "</ul></div>")
    else:
        caja = ("<div style='background:#e8f5e9;border:1px solid #a5d6a7;"
                "border-radius:8px;padding:10px;margin:0 0 16px;color:#256029'>"
                "Sin disparos — todo en orden.</div>")

    th = "style='padding:8px;text-align:left'"
    tabla = ("<table style='width:100%;border-collapse:collapse;font-size:13px'>"
             f"<thead><tr style='background:#1f2a44;color:#fff'>"
             f"<th {th}>Posición</th><th {th}>Actual</th><th {th}>Ref.</th>"
             f"<th {th}>P/L</th><th {th}>Detalle / niveles</th></tr></thead>"
             f"<tbody>{''.join(filas)}</tbody></table>")

    return (f"<div style='font-family:Arial,Helvetica,sans-serif;max-width:680px;"
            f"color:#222'><h2 style='margin:0 0 4px'>Monitor de posiciones</h2>"
            f"<div style='color:#666;margin-bottom:14px'>{_esc(r['hora'])}</div>"
            f"{caja}{tabla}</div>")


def enviar_email(asunto: str, cuerpo: str, destino: str, html: str | None = None) -> str:
    """Envia por Resend si hay clave. Devuelve el estado, nunca lanza.

    Si `html` viene, se manda tambien la version HTML (para botones clicables);
    el `text` queda como respaldo para clientes que no rendericen HTML.
    """
    key = os.environ.get("RESEND_API_KEY") or ""
    if not key:
        env = REPO / "API" / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("RESEND_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        return "email no enviado: falta RESEND_API_KEY en API/.env"
    _pie = ("\n\n—\nEste sistema solo informa. "
            "No ejecuta ordenes: tu decides y operas en tu broker.")
    try:
        import httpx
        payload = {"from": "Warren Buffett Jr <onboarding@resend.dev>",
                   "to": [destino], "subject": asunto,
                   "text": cuerpo + _pie}
        if html:
            payload["html"] = html + (
                "<hr><p style='font-size:12px;color:#888'>Este sistema solo "
                "informa. No ejecuta ordenes: tu decides y operas en tu broker.</p>")
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json=payload,
            timeout=25.0)
        return f"email enviado a {destino}" if r.status_code < 300 else \
               f"email fallo ({r.status_code})"
    except Exception as e:  # noqa: BLE001
        return f"email fallo: {type(e).__name__}"


def main() -> int:
    # --resumen: informe diario, se envia aunque no haya disparos (cierre de
    # mercado). --forzar: igual, para pruebas manuales.
    resumen = "--resumen" in sys.argv
    forzar = "--forzar" in sys.argv
    r = revisar()
    print(texto(r))
    if r.get("error"):
        # Un fallo de Schwab deja el monitoreo ciego: eso SI hay que avisarlo.
        if resumen:
            cfg = _cargar(POSICIONES, {})
            enviar_email("Warren Buffett Jr — MONITOREO CAIDO",
                         f"El monitor no pudo revisar tus posiciones:\n\n{r['error']}\n\n"
                         "Mientras tanto no hay vigilancia automatica.",
                         cfg.get("email_destino", ""))
        return 1
    if r["disparos"] or forzar or resumen:
        if r["disparos"]:
            cab = r["disparos"][0].split(":")[0]
        else:
            cab = "resumen del dia" if resumen else "reporte"
        print(enviar_email(f"Warren Buffett Jr — {cab}", texto(r),
                           r["email_destino"], html=html_reporte(r)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
