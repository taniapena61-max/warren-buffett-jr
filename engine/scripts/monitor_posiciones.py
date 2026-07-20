"""Monitor de posiciones de Tania — avisa al +25% y al +50% sobre el costo.

Lee `API/posiciones.json`, consulta Schwab en vivo y decide si hay algo que
avisar. Tres disparadores:

  * ALERTA  — la posicion alcanza el +25% sobre lo pagado.
  * IDEAL   — alcanza el +50% (nivel de cierre ideal declarado por Tania).
  * MOVIMIENTO — se mueve mas de X% desde la ultima revision.

Salida: texto para el chat/notificacion, y email por Resend SOLO si existe
RESEND_API_KEY. Sin esa clave el script sigue funcionando y no falla — lo dice
y ya. Nunca ejecuta ordenes: informa, Tania decide y opera en su broker.

Uso:
    python scripts/monitor_posiciones.py            # revisa y reporta
    python scripts/monitor_posiciones.py --forzar   # reporta aunque no dispare
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


def revisar() -> dict:
    """Consulta Schwab y evalua cada posicion contra sus umbrales."""
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

    filas, disparos, nuevo_estado = [], [], {}
    for p in cfg["posiciones"]:
        try:
            q = sch.quote(p["simbolo_schwab"])
        except Exception as e:  # noqa: BLE001 — una falla no debe tumbar el resto
            filas.append({"id": p["id"], "error": f"{type(e).__name__}"})
            continue
        if not q or q.get("mark") is None:
            filas.append({"id": p["id"], "error": "sin cotizacion"})
            continue

        mark = float(q["mark"])
        costo = float(p["costo_por_accion"])
        contratos = int(p.get("contratos", 1))
        pl_pct = (mark / costo - 1) * 100
        pl_usd = (mark - costo) * 100 * contratos

        fila = {
            "id": p["id"], "descripcion": p["descripcion"],
            "costo": costo, "mark": round(mark, 2),
            "pl_pct": round(pl_pct, 1), "pl_usd": round(pl_usd, 0),
            "objetivo_alerta": round(costo * (1 + alerta_pct / 100), 2),
            "objetivo_ideal": round(costo * (1 + ideal_pct / 100), 2),
            "subyacente": q.get("underlyingPrice"),
            "delta": q.get("delta"), "theta": q.get("theta"),
        }

        if pl_pct >= ideal_pct:
            disparos.append(f"IDEAL +{ideal_pct}%: {p['descripcion']} en ${mark:.2f} ({pl_pct:+.1f}%)")
        elif pl_pct >= alerta_pct:
            disparos.append(f"ALERTA +{alerta_pct}%: {p['descripcion']} en ${mark:.2f} ({pl_pct:+.1f}%)")

        antes = previo.get(p["id"], {}).get("mark")
        if antes:
            cambio = (mark / float(antes) - 1) * 100
            fila["cambio_desde_revision"] = round(cambio, 1)
            if abs(cambio) >= mov_pct:
                disparos.append(
                    f"MOVIMIENTO {cambio:+.1f}%: {p['descripcion']} "
                    f"${float(antes):.2f} -> ${mark:.2f}")

        nuevo_estado[p["id"]] = {"mark": mark, "visto": datetime.now().isoformat()}
        filas.append(fila)

    ESTADO.write_text(json.dumps(nuevo_estado, indent=2), encoding="utf-8")
    return {"hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "filas": filas, "disparos": disparos,
            "email_destino": cfg.get("email_destino")}


def texto(r: dict) -> str:
    if r.get("error"):
        return f"Monitor: {r['error']}"
    out = [f"Monitor de posiciones — {r['hora']}", ""]
    for f in r["filas"]:
        if f.get("error"):
            out.append(f"  {f['id']}: {f['error']}")
            continue
        out.append(
            f"  {f['descripcion']}\n"
            f"    costo ${f['costo']:.2f} -> mark ${f['mark']:.2f}  "
            f"({f['pl_pct']:+.1f}%, ${f['pl_usd']:+,.0f})\n"
            f"    avisar en ${f['objetivo_alerta']:.2f} · ideal ${f['objetivo_ideal']:.2f}"
            + (f"  [PLTR ${f['subyacente']:.2f}]" if f.get("subyacente") else ""))
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
                  "to": [destino], "subject": asunto, "text": cuerpo},
            timeout=20.0)
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
        asunto = ("Warren Buffett Jr — " +
                  (r["disparos"][0].split(":")[0] if r["disparos"] else "reporte"))
        print(enviar_email(asunto, texto(r), r["email_destino"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
