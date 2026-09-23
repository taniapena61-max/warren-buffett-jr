# -*- coding: utf-8 -*-
"""
VANNA GUARD  (Roos #10) — dos señales de vanna:
  (A) VIX-FADE = REBOTE: si el VIX SALTA y luego se DESVANECE, el desplazamiento fue
      vol-driven -> el precio rebota casi donde empezo. Anticipar reversion al nivel pre-spike.
  (B) PRE-EVENTO = VENTA MECANICA: vol baja + evento macro (Fed) enfrente -> el MM VENDE
      futuros (vanna). No comprometerse alcista de mas; posicionar para la venta / esperar
      el rebote post-evento.

Autocontenido: lee VIX spot de Tito y mantiene su propio log intradia (historial/vix_intradia.jsonl)
para detectar el spike->fade. El calendario se lee de historial/eventos_macro.json (opcional).
Uso: py scripts/vanna_guard.py [SYM]   Solo informa.
"""
import sys, json, urllib.request
from pathlib import Path
from datetime import date, datetime

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"
REPO = Path(__file__).resolve().parent.parent
VIXLOG = REPO / "historial" / "vix_intradia.jsonl"
EVENTOS = REPO / "historial" / "eventos_macro.json"
VIX_BAJO = 16.0        # "vol baja" para el pre-evento
FADE_MIN = 1.2         # el VIX cayo al menos esto desde el pico de hoy = fade real


def getj(path):
    import time
    for _ in range(3):
        try:
            with urllib.request.urlopen(BASE + path, timeout=15) as r:
                d = json.load(r)
            if d:
                return d
        except Exception:
            pass
        time.sleep(1.2)
    return {}


def vix_now():
    d = getj(f"/api/salud?symbol={SYM}")
    for l in d.get("lentes", []):
        if l.get("lente") == "VIX / volatilidad":
            try:
                return float(l.get("detalle", "").split("VIX")[1].split("·")[0].strip())
            except Exception:
                return None
    a = getj(f"/api/odte?symbol={SYM}").get("analysis", {})
    return a.get("vix")


def log_vix(v):
    try:
        with VIXLOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.now().isoformat(), "vix": v}) + "\n")
    except Exception:
        pass


def vix_hoy():
    day = date.today().isoformat()
    out = []
    try:
        for line in VIXLOG.read_text(encoding="utf-8").splitlines():
            o = json.loads(line)
            if str(o.get("ts", "")).startswith(day) and o.get("vix"):
                out.append(float(o["vix"]))
    except Exception:
        pass
    return out


def prox_evento():
    try:
        evs = json.loads(EVENTOS.read_text(encoding="utf-8")).get("eventos", [])
        hoy = date.today()
        fut = []
        for e in evs:
            try:
                d = date.fromisoformat(e.get("fecha"))
                if d >= hoy:
                    fut.append((d, e.get("nombre", "evento")))
            except Exception:
                pass
        fut.sort()
        return fut[0] if fut else None
    except Exception:
        return None


def main():
    v = vix_now()
    if v is None:
        print("[vanna_guard] sin VIX (Tito?)."); return 1
    log_vix(v)
    serie = vix_hoy()
    pico = max(serie) if serie else v
    print("=" * 60)
    print(f"VANNA GUARD — VIX {v:.2f} | pico hoy {pico:.2f} | lecturas {len(serie)}")
    # (A) VIX-FADE
    caida = pico - v
    if caida >= FADE_MIN:
        print(f"  (A) ** VIX-FADE = REBOTE ** el VIX subio a {pico:.2f} y se desvanece a {v:.2f} "
              f"(-{caida:.1f}).")
        print(f"      El drop fue vol-driven -> anticipa REVERSION del precio hacia el nivel PRE-spike.")
        print(f"      Entrada: posicionarse en el nivel de donde salio (rebote), no perseguir.")
    else:
        print(f"  (A) VIX-fade: sin fade relevante hoy (caida {caida:.1f} < {FADE_MIN}).")
    # (B) PRE-EVENTO
    ev = prox_evento()
    if ev:
        d, nombre = ev
        dias = (d - date.today()).days
        if dias <= 2 and v <= VIX_BAJO:
            print(f"  (B) ** PRE-EVENTO = VENTA MECANICA ** {nombre} en {dias}d + VIX bajo ({v:.1f}).")
            print(f"      Vanna: el MM tiende a VENDER futuros antes (la vol va a subir). NO te")
            print(f"      comprometas alcista de mas; posiciona para la venta / espera el rebote post-evento.")
        else:
            print(f"  (B) proximo evento: {nombre} en {dias}d (VIX {v:.1f}). "
                  + ("vol no tan baja" if v > VIX_BAJO else "aun lejos"))
    else:
        print(f"  (B) [!] sin calendario -> registrar proximo FOMC/CPI en historial/eventos_macro.json")
        print(f'      formato: {{"eventos":[{{"fecha":"2026-10-28","nombre":"FOMC"}}]}}')
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
