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
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wbj.config import load_settings  # noqa: E402
from wbj.providers.schwab import SchwabProvider  # noqa: E402

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


def revisar() -> dict:
    cfg = _cargar(POSICIONES, {})
    if not cfg.get("posiciones"):
        return {"error": "no hay posiciones configuradas en API/posiciones.json"}

    s = load_settings()
    sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                         s.schwab_callback_url, s.schwab_token_path)
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
            fila = {"id": p["id"], "desc": p["descripcion"], "tipo": tipo,
                    "prima": prima, "mark": round(mark, 2),
                    "ganado_pct": round(ganado_pct, 1),
                    "pl_usd": round((prima - mark) * 100 * n, 0),
                    "strike": strike, "subyacente": subyacente,
                    "valor_temporal": round(float(vt), 2) if vt is not None else None,
                    "delta": q.get("delta"),
                    "equilibrio": round(strike - prima, 2)}
            if subyacente is not None:
                fila["itm"] = round(strike - float(subyacente), 2)

            # 1) asignacion temprana: lo que de verdad la provoca
            if vt is not None and float(vt) < vt_critico and \
                    subyacente is not None and float(subyacente) < strike:
                disparos.append(
                    f"RIESGO ASIGNACION TEMPRANA: {p['descripcion']} — valor "
                    f"temporal ${float(vt):.2f} (bajo ${vt_critico:.2f}) e ITM. "
                    f"Pueden ejercerte antes del vencimiento.")
            # 2) profundidad ITM relevante
            if subyacente is not None and float(subyacente) < strike:
                prof = (strike - float(subyacente)) / strike * 100
                if prof >= 10:
                    disparos.append(
                        f"MUY ITM: {p['descripcion']} — {p['simbolo_schwab'][:4]} "
                        f"en ${float(subyacente):.2f}, {prof:.0f}% bajo el strike "
                        f"${strike:.0f}.")
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
        filas.append(fila)

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
        if t == "accion":
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


def enviar_email(asunto: str, cuerpo: str, destino: str) -> str:
    """Envia por Resend si hay clave. Devuelve el estado, nunca lanza."""
    key = os.environ.get("RESEND_API_KEY") or ""
    if not key:
        env = REPO / "API" / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("RESEND_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        return "email no enviado: falta RESEND_API_KEY en API/.env"
    try:
        import httpx
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json={"from": "Warren Buffett Jr <onboarding@resend.dev>",
                  "to": [destino], "subject": asunto,
                  "text": cuerpo + "\n\n—\nEste sistema solo informa. "
                          "No ejecuta ordenes: tu decides y operas en tu broker."},
            timeout=25.0)
        return f"email enviado a {destino}" if r.status_code < 300 else \
               f"email fallo ({r.status_code})"
    except Exception as e:  # noqa: BLE001
        return f"email fallo: {type(e).__name__}"


def main() -> int:
    forzar = "--forzar" in sys.argv
    r = revisar()
    print(texto(r))
    if r.get("error"):
        return 1
    if r["disparos"] or forzar:
        cab = r["disparos"][0].split(":")[0] if r["disparos"] else "reporte"
        print(enviar_email(f"Warren Buffett Jr — {cab}", texto(r), r["email_destino"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
