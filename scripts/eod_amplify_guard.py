# -*- coding: utf-8 -*-
"""
EOD AMPLIFY GUARD  (Roos #12) — ETFs apalancados 2x/3x amplifican el CIERRE.
Los ETF apalancados rebalancean HACIA EL CIERRE en la MISMA direccion del dia
-> en dia TENDENCIAL la ultima hora se ACELERA. Regla: NO fadear el cierre en dia
trending (eso mato el fly 7750 el 22-sep). Ir a favor o esperar.

Dispara solo en la ventana de cierre (minClose <= VENTANA) y si el dia es tendencial.
Uso: py scripts/eod_amplify_guard.py [SYM]    Solo informa.
"""
import sys, json, urllib.request

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"
VENTANA = 75          # min al cierre para activar el guard
TREND_PCT = 0.35      # % desde el open que cuenta como tendencia
TREND_ABS = 22        # o puntos absolutos SPX


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


def open_hoy():
    """Precio de apertura de hoy (primera vela) via odte->history proxy no hay;
    usar rangeClose/5min como fallback. Devuelve None si no se puede."""
    d = getj(f"/api/odte?symbol={SYM}")
    a = d.get("analysis", d)
    # Tito no expone el open directo; aproximar con el VWAP si esta, si no None.
    return a


def main():
    a = open_hoy()
    spot = a.get("spot")
    mtc = a.get("minutesToClose")
    if not spot or mtc is None:
        print("[eod_guard] sin spot/minClose (Tito?)."); return 1
    spot = float(spot)
    if mtc < 0:
        print(f"[eod_guard] mercado CERRADO (min_cierre {mtc}). El guard corre en la sesion.")
        return 0
    # tendencia: usar pin_intradia (spots de hoy) para ver el movimiento del dia
    import pathlib, datetime
    src = pathlib.Path(__file__).resolve().parent.parent / "historial" / "pin_intradia.jsonl"
    day = datetime.date.today().isoformat()
    spots = []
    try:
        for line in src.read_text(encoding="utf-8").splitlines():
            o = json.loads(line)
            if str(o.get("ts", "")).startswith(day) and o.get("spot"):
                spots.append(float(o["spot"]))
    except Exception:
        pass
    print("=" * 60)
    print(f"EOD AMPLIFY GUARD — {SYM} | spot {spot:.1f} | min_cierre {mtc}")
    if mtc > VENTANA:
        print(f"  Fuera de la ventana de cierre (>{VENTANA}min). Sin alerta.")
        print("=" * 60); return 0
    if len(spots) < 3:
        print("  [!] Pocos spots de hoy para medir tendencia; revisar a ojo el open vs ahora.")
        print("=" * 60); return 0
    op = spots[0]
    mov = spot - op
    pct = 100 * mov / op
    trending = abs(mov) >= TREND_ABS or abs(pct) >= TREND_PCT
    direc = "ARRIBA" if mov > 0 else "ABAJO"
    print(f"  Movimiento del dia: open~{op:.0f} -> {spot:.0f} = {mov:+.0f}pt ({pct:+.2f}%)")
    if trending:
        print(f"  ** DIA TENDENCIAL {direc} + ventana de cierre = ETF 2x/3x AMPLIFICAN el EOD **")
        print(f"  -> NO fadear el cierre (no vender fly/vertical contra {direc}).")
        print(f"     Si operas: A FAVOR de {direc} (vertical) o ESPERAR. (Esto mato el fly 7750 el 22-sep.)")
    else:
        print(f"  Dia NO tendencial (chop) -> el fly de cierre/pin es valido; el EOD no amplifica.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
