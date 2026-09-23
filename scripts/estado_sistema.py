#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ESTADO DEL SISTEMA — chequeo de arranque (correr al INICIAR cada sesión).
Recarga y verifica TODO lo construido para que nada se "olvide" ni se rompa
entre días. Es la red de seguridad contra el "paso adelante, paso atrás".

Verifica: tareas programadas · posiciones · lentes base (salud) · lentes extra ·
cookie MS · errores recientes en logs. Salida clara con OK/ATENCIÓN.
Uso: engine\\.venv\\Scripts\\python.exe scripts\\estado_sistema.py
"""
import json, subprocess, urllib.request, sys
from datetime import datetime, date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(r"C:\Users\tania\Desktop\warren-buffett-jr")
OK = "✅"; WARN = "⚠️"; BAD = "❌"


def hdr(t): print(f"\n{'='*60}\n  {t}\n{'='*60}")


def check_tareas():
    hdr("1) TAREAS PROGRAMADAS (deben correr solas)")
    try:
        out = subprocess.run(["schtasks", "/query", "/fo", "csv", "/nh"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception as e:
        print(f"  {WARN} no pude consultar schtasks: {e}"); return
    wbj = [l for l in out.splitlines() if "WBJ" in l]
    seen = set()
    for l in wbj:
        parts = [p.strip('"') for p in l.split('","')]
        name = parts[0].strip('"').lstrip("\\"); state = parts[-1].strip('"') if len(parts) > 2 else "?"
        if "WBJ" not in name or name in seen:
            continue
        seen.add(name)
        mark = OK if state in ("Ready", "Running", "Listo", "En ejecución") else WARN
        print(f"  {mark} {name}: {state}")
    if not seen:
        print(f"  {WARN} no se encontraron tareas WBJ")


def check_posiciones():
    hdr("2) POSICIONES ABIERTAS (posiciones.json)")
    try:
        d = json.load(open(REPO / "API" / "posiciones.json", encoding="utf-8"))
        for p in d["posiciones"]:
            print(f"  {OK} {p['id']}")
        print(f"  → {len(d['posiciones'])} posiciones monitoreadas")
    except Exception as e:
        print(f"  {BAD} posiciones.json ROTO: {e}")


def check_salud():
    hdr("3) LENTES BASE (/api/salud SPX)")
    try:
        with urllib.request.urlopen("http://localhost:3000/api/salud?symbol=SPX", timeout=25) as r:
            d = json.load(r)
        for l in d["lentes"]:
            mark = OK if l["ok"] else WARN
            print(f"  {mark} {l['lente']}")
        fail = d.get("fallando") or []
        if fail:
            print(f"  → OJO fallando: {fail}  (post-cierre el GEX propio da 'sin muros', normal)")
    except Exception as e:
        print(f"  {WARN} Tito/salud no responde (¿está corriendo npm start?): {e}")


def check_lentes_extra():
    hdr("4) LENTES EXTRA (script)")
    p = REPO / "scripts" / "lentes" / "lentes_extra.py"
    print(f"  {OK if p.exists() else BAD} lentes_extra.py {'presente' if p.exists() else 'FALTA'}")
    print("  (8 lentes: notional walls, net premium, VIX, sectores, order book side, order structure, premium sellers, OI build-up)")


def check_cookie():
    hdr("5) COOKIE MARKETSNACK")
    f = REPO / "API" / "marketsnack_cookie.txt"
    if not f.exists():
        print(f"  {BAD} falta el archivo de cookie"); return
    edad = datetime.now().timestamp() - f.stat().st_mtime
    horas = edad / 3600
    mark = OK if horas < 24 else WARN
    print(f"  {mark} cookie actualizada hace {horas:.1f}h (auto-renovación keepalive)")


def check_errores():
    hdr("6) ERRORES RECIENTES EN LOGS (hoy)")
    logdir = REPO / "logs"
    hoy = date.today().strftime("%Y%m%d")
    hits = 0
    if logdir.exists():
        for f in logdir.glob(f"*{hoy}*.log"):
            try:
                for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                    if any(w in line for w in ("Traceback", "Error", "ERROR", "fallo")):
                        print(f"  {WARN} {f.name}: {line[:80]}"); hits += 1
                        if hits >= 8:
                            break
            except Exception:
                pass
    print(f"  {'⚠️ revisar' if hits else OK} {hits} líneas de error encontradas hoy")


def _en_hora_mercado():
    """True si es día hábil y estamos entre 9:30 y 16:00 ET (la máquina ya es ET)."""
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return 9 * 60 + 30 <= t <= 16 * 60


def check_frescura():
    """GATE de frescura: task Ready/200 NO es salud. Salud = el dato es de HOY.
    El stale silencioso produce números creíbles pero falsos → cuesta dinero."""
    hdr("7) FRESCURA DE DATOS (¿los datos son de HOY?)  ← el que cuesta dinero")
    market = _en_hora_mercado()
    marca_stale = BAD if market else WARN  # fuera de hora, stale es esperado

    # 1) Nancy VWAP — debe traer barras de HOY (Schwab con period=N da días cerrados)
    venv = REPO / "engine" / ".venv" / "Scripts" / "python.exe"
    try:
        out = subprocess.run([str(venv), str(REPO / "scripts" / "vwap_ds_bands.py"), "SPX"],
                             capture_output=True, text=True, timeout=60).stdout
        low = out.lower()
        stale = ("ojo barras" in low) or ("lag post-cierre" in low) or ("stale" in low)
        line0 = out.splitlines()[0][:72] if out.strip() else ""
        if not out.strip():
            print(f"  {BAD} Nancy VWAP: SIN SALIDA (lente caída)")
        elif stale:
            print(f"  {marca_stale} Nancy VWAP: STALE (no es de hoy) → {line0}")
        else:
            print(f"  {OK} Nancy VWAP (hoy): {line0}")
    except Exception as e:
        print(f"  {BAD} Nancy VWAP: error al correr ({e})")

    # 2) Lentes de salud que reportan dato VIEJO en su detalle
    stale_words = ("no es de hoy", "stale", "vencid", "lag", "pegad", "viejo", "atrasad")
    try:
        with urllib.request.urlopen("http://localhost:3000/api/salud?symbol=SPX", timeout=25) as r:
            d = json.load(r)
        flagged = [l for l in d["lentes"]
                   if any(w in (l.get("detalle") or "").lower() for w in stale_words)]
        if flagged:
            for l in flagged:
                print(f"  {marca_stale} {l['lente']}: {(l.get('detalle') or '')[:70]}")
        else:
            print(f"  {OK} ninguna lente de salud reporta dato viejo")
    except Exception as e:
        print(f"  {WARN} no pude revisar salud para frescura: {e}")

    # 3) Estrade en vivo (SS)
    try:
        with urllib.request.urlopen("http://localhost:3000/api/straddle?ticker=SPX", timeout=15) as r:
            s = json.load(r)
        if s.get("straddle"):
            print(f"  {OK} estrade en vivo: {s.get('straddle')} (exp {s.get('exp')})")
        else:
            print(f"  {WARN} estrade sin valor")
    except Exception as e:
        print(f"  {WARN} estrade no responde: {e}")

    if market:
        print("  → EN HORA DE MERCADO: cualquier ❌ aquí = NO usar esa lente hasta arreglarla.")
    else:
        print("  → fuera de hora de mercado: 'no es de hoy' puede ser normal (revisar al abrir).")


def main():
    print(f"\n{'#'*60}\n#  ESTADO DEL SISTEMA — {datetime.now():%Y-%m-%d %H:%M}\n{'#'*60}")
    check_tareas()
    check_posiciones()
    check_salud()
    check_lentes_extra()
    check_cookie()
    check_errores()
    check_frescura()
    check_entradas()
    check_flip_levels()
    check_selector()
    check_vanna()
    check_eod()
    check_trampolin()
    print(f"\n{'#'*60}\n#  Fin del chequeo. Corre esto al iniciar cada sesión.\n{'#'*60}")
    return 0


def check_trampolin():
    """13) TRAMPOLIN (Roos): recompra forzada al expirar = rebote desde el put wall."""
    hdr("13) TRAMPOLIN GUARD (rebote post-vencimiento por recompra forzada — Roos)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "trampolin_guard.py"), "SPX"],
                           capture_output=True, text=True, timeout=40)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} trampolin_guard sin salida (¿Tito?)")
    except Exception as e:
        print(f"  {WARN} no pude correr trampolin_guard.py: {e}")


def check_vanna():
    """11) VANNA (Roos): VIX-fade = rebote · pre-evento = venta mecanica."""
    hdr("11) VANNA GUARD (VIX-fade rebote / pre-Fed venta mecanica — Roos)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "vanna_guard.py"), "SPX"],
                           capture_output=True, text=True, timeout=40)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} vanna_guard sin salida (¿Tito?)")
    except Exception as e:
        print(f"  {WARN} no pude correr vanna_guard.py: {e}")


def check_eod():
    """12) EOD AMPLIFY GUARD (Roos): ETF 2x/3x amplifican el cierre; no fadear dia trending."""
    hdr("12) EOD AMPLIFY GUARD (no fadear el cierre en dia trending — Roos)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "eod_amplify_guard.py"), "SPX"],
                           capture_output=True, text=True, timeout=40)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} eod_guard sin salida (¿Tito?)")
    except Exception as e:
        print(f"  {WARN} no pude correr eod_amplify_guard.py: {e}")


def check_selector():
    """10) SELECTOR DEL MÉTODO DEL DÍA — condicion -> metodo -> entrada (SIN TRADES NO EXISTIMOS)."""
    hdr("10) METODO DEL DIA + SETUPS EJECUTABLES (selector_metodo.py)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "selector_metodo.py"), "SPX"],
                           capture_output=True, text=True, timeout=50)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} selector sin salida (¿Tito/VS3D?)")
    except Exception as e:
        print(f"  {WARN} no pude correr selector_metodo.py: {e}")


def check_flip_levels():
    """9) Niveles de FLIP del MM (rebote abajo / rechazo arriba) — Roos/VS3D."""
    hdr("9) FLIP LEVELS (rebote/rechazo mecanico del MM — Roos)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "flip_level.py"), "SPX"],
                           capture_output=True, text=True, timeout=40)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} flip_level sin salida (¿Tito/VS3D?)")
    except Exception as e:
        print(f"  {WARN} no pude correr flip_level.py: {e}")


def check_entradas():
    """Recuerda los pasos de cada metodo de entrada + nucleo (checklist_entradas.py)."""
    hdr("8) CHECKLIST DE ENTRADAS (pasos de cada metodo + no mezclar)")
    try:
        import subprocess
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "checklist_entradas.py")],
                           capture_output=True, text=True, timeout=40)
        out = (r.stdout or "").strip()
        print(out if out else f"  {WARN} checklist sin salida")
    except Exception as e:
        print(f"  {WARN} no pude correr checklist_entradas.py: {e}")


if __name__ == "__main__":
    sys.exit(main())
