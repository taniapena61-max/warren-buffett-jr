"""Strikes de SPX por delta a la apertura — para las decisiones de spreads de Tania.

Cada mañana (o cuando se corra) consulta la cadena de opciones de SPX en Schwab
y encuentra, para calls y puts, los strikes más cercanos a delta 0.20 / 0.25 /
0.30 — los strikes cortos típicos de sus verticales/mariposas/condors.

Muestra el 0DTE (mismo día) y el siguiente vencimiento, porque en 0DTE los
strikes de delta se agolpan (el delta salta rápido entre strikes de 5 pts cerca
del vencimiento) y ver un tenor más largo da separación útil.

- Datos 100% de Schwab (delta que calcula el propio bróker).
- Envía email por Resend si hay clave, y agrega el resultado al diario del día.
- Solo informa. No es recomendación ni orden.

Uso:
    python scripts/deltas_apertura_spx.py                 # SPX, 2 vencimientos
    python scripts/deltas_apertura_spx.py --simbolo IREN  # otro subyacente
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wbj.config import load_settings  # noqa: E402
from wbj.providers.schwab import SchwabProvider  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
_CHAINS = "https://api.schwabapi.com/marketdata/v1/chains"
DELTAS = (0.20, 0.25, 0.30)


def _strike_para_delta(mapa: dict, exp: str, objetivo: float):
    """Strike cuyo |delta| más se acerca a `objetivo`. (strike, delta) o None."""
    best = None
    for k, arr in mapa.get(exp, {}).items():
        o = arr[0]
        dl = o.get("delta")
        if not isinstance(dl, (int, float)) or abs(dl) > 1:
            continue  # -999/NaN de Schwab
        diff = abs(abs(dl) - objetivo)
        if best is None or diff < best[0]:
            best = (diff, float(k), float(dl))
    return (best[1], best[2]) if best else None


def reporte(simbolo: str = "$SPX", vencimientos: int = 2) -> dict:
    s = load_settings()
    sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                         s.schwab_callback_url, s.schwab_token_path,
                         history_dir=s.history_dir)
    if not sch.available:
        return {"error": "Schwab no autorizado — renueva con 'Renovar Schwab.bat'"}
    try:
        spot = sch.quote(simbolo)
        S = float(spot["lastPrice"])
        tok = sch._valid_access_token()
        from datetime import timedelta
        hoy = date.today()
        r = httpx.get(_CHAINS, headers={"Authorization": f"Bearer {tok}"},
                      params={"symbol": simbolo, "contractType": "ALL",
                              "includeUnderlyingQuote": "false",
                              # acotar el rango: SPX completo es enorme y da 502
                              "fromDate": hoy.isoformat(),
                              "toDate": (hoy + timedelta(days=9)).isoformat()},
                      timeout=30)
        if r.status_code != 200:
            return {"error": f"cadena de opciones no disponible ({r.status_code})"}
        d = r.json()
    except Exception as e:  # noqa: BLE001
        return {"error": f"fallo consultando Schwab: {type(e).__name__}"}

    calls, puts = d.get("callExpDateMap", {}), d.get("putExpDateMap", {})
    exps = list(calls.keys())[:vencimientos]
    bloques = []
    for exp in exps:
        fecha, dte = exp.split(":")
        filas = []
        for obj in DELTAS:
            c = _strike_para_delta(calls, exp, obj)
            p = _strike_para_delta(puts, exp, obj)
            filas.append({"delta": obj,
                          "call": c[0] if c else None, "call_d": c[1] if c else None,
                          "put": p[0] if p else None, "put_d": p[1] if p else None})
        bloques.append({"fecha": fecha, "dte": int(dte), "filas": filas})
    return {"simbolo": simbolo, "spot": round(S, 2),
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M"), "bloques": bloques}


def texto(r: dict) -> str:
    if r.get("error"):
        return f"Deltas de apertura: {r['error']}"
    out = [f"Strikes por delta — {r['simbolo']} ${r['spot']:.2f}  ({r['hora']})", ""]
    for b in r["bloques"]:
        out.append(f"Vencimiento {b['fecha']} ({b['dte']} DTE):")
        out.append(f"  {'delta':>6}  {'CALL':>6} {'(real)':>8}   {'PUT':>6} {'(real)':>8}")
        for f in b["filas"]:
            cd = f"{f['call_d']:+.2f}" if f["call_d"] is not None else "n/d"
            pd = f"{f['put_d']:+.2f}" if f["put_d"] is not None else "n/d"
            cs = f"{f['call']:.0f}" if f["call"] is not None else "n/d"
            ps = f"{f['put']:.0f}" if f["put"] is not None else "n/d"
            out.append(f"  {f['delta']:>6.2f}  {cs:>6} {cd:>8}   {ps:>6} {pd:>8}")
        out.append("")
    out.append("Solo informativo — no es recomendacion ni orden.")
    return "\n".join(out)


def _enviar_email(asunto: str, cuerpo: str) -> str:
    env = REPO / "API" / ".env"
    key = os.environ.get("RESEND_API_KEY") or ""
    dest = "taniapena61@gmail.com"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("RESEND_API_KEY=") and not key:
                key = line.split("=", 1)[1].strip()
            if line.startswith("EMAIL_TO="):
                dest = line.split("=", 1)[1].strip() or dest
    if not key:
        return "email no enviado: falta RESEND_API_KEY"
    try:
        resp = httpx.post("https://api.resend.com/emails",
                          headers={"Authorization": f"Bearer {key}"},
                          json={"from": "Warren Buffett Jr <onboarding@resend.dev>",
                                "to": [dest], "subject": asunto, "text": cuerpo},
                          timeout=25.0)
        return f"email enviado a {dest}" if resp.status_code < 300 else \
               f"email fallo ({resp.status_code})"
    except Exception as e:  # noqa: BLE001
        return f"email fallo: {type(e).__name__}"


def _al_diario(r: dict) -> None:
    """Agrega los strikes por delta al diario de SPX del día."""
    if r.get("error") or r["simbolo"] != "$SPX":
        return
    diario = REPO / "historial" / "spx_diario" / f"{date.today().isoformat()}.md"
    diario.parent.mkdir(parents=True, exist_ok=True)
    bloque = "\n## Strikes por delta a la apertura (Schwab)\n\n```\n" + \
             texto(r) + "\n```\n"
    with diario.open("a", encoding="utf-8") as fh:
        fh.write(bloque)


def main() -> int:
    simbolo = "$SPX"
    if "--simbolo" in sys.argv:
        simbolo = sys.argv[sys.argv.index("--simbolo") + 1].upper()
        if not simbolo.startswith("$") and simbolo in ("SPX", "VIX", "NDX", "RUT"):
            simbolo = "$" + simbolo
    r = reporte(simbolo)
    print(texto(r))
    if r.get("error"):
        return 1
    _al_diario(r)
    print(_enviar_email(f"Strikes por delta — {r['simbolo']} apertura", texto(r)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
