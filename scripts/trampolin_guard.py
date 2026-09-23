# -*- coding: utf-8 -*-
"""
TRAMPOLIN GUARD  (Roos #11) — recompra FORZADA al expirar = rebote.
Roos: "cuanto MAS vende el MM (cubriendo cortos hasta un nivel), MAS compra OBLIGATORIA
hay cuando esa posicion EXPIRA" -> trampolin/rebote al alza tras el vencimiento.
Setup: cerca de un vencimiento grande (OPEX 3er viernes / quad-witch Mar-Jun-Sep-Dic) +
put wall pesado abajo donde el MM estuvo vendiendo (γ− o spot bajo el flip) -> anticipar
REBOTE desde ~putWall DESPUES del vencimiento.

Uso: py scripts/trampolin_guard.py [SYM]   Solo informa.
"""
import sys, json, urllib.request
from datetime import date, timedelta

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"


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


def tercer_viernes(y, m):
    d = date(y, m, 1)
    fri = [d + timedelta(days=i) for i in range(31)
           if (d + timedelta(days=i)).month == m and (d + timedelta(days=i)).weekday() == 4]
    return fri[2]


def prox_opex(hoy):
    """Proximo 3er viernes (OPEX) >= hoy, y si es quad-witch (Mar/Jun/Sep/Dic)."""
    y, m = hoy.year, hoy.month
    for _ in range(3):
        tv = tercer_viernes(y, m)
        if tv >= hoy:
            return tv, (m in (3, 6, 9, 12))
        m += 1
        if m > 12:
            m = 1; y += 1
    return None, False


def main():
    a = getj(f"/api/odte?symbol={SYM}").get("analysis", {})
    spot = a.get("spot")
    if not spot:
        print("[trampolin] sin spot (Tito?)."); return 1
    spot = float(spot)
    putw = a.get("putWall"); topput = a.get("topPutStrike"); flip = a.get("flip")
    reg = str(a.get("regime", "")).lower()
    ng = (a.get("totalNetGex") or 0) / 1e9
    hoy = date.today()
    opex, quad = prox_opex(hoy)
    dias = (opex - hoy).days if opex else None
    print("=" * 62)
    print(f"TRAMPOLIN GUARD — {SYM} | spot {spot:.1f} | putWall {putw} | flip "
          f"{round(flip,1) if isinstance(flip,(int,float)) else flip} | netGEX {ng:+.1f}B")
    print(f"  proximo vencimiento grande: {opex} ({'QUAD-WITCH' if quad else 'OPEX mensual'}) en {dias}d")
    cerca = dias is not None and dias <= 3
    # "el MM estuvo vendiendo hasta el nivel" ~ spot bajo el flip (γ− local) o regime negativo
    vendiendo = (isinstance(flip, (int, float)) and spot < flip) or reg == "negative" or ng < 0
    nivel = putw or topput
    if cerca and vendiendo and nivel:
        print(f"  ** TRAMPOLIN ARMADO ** vencimiento en {dias}d + MM vendiendo (γ−/bajo flip) + "
              f"put wall {nivel}.")
        print(f"  -> Tras el vencimiento, la RECOMPRA FORZADA del MM = REBOTE al alza desde ~{nivel}.")
        print(f"     Entrada: posicionarse para el rebote en {nivel} (no perseguir la caida previa).")
    elif cerca and nivel:
        print(f"  Vencimiento cerca ({dias}d) pero el MM NO esta claramente vendiendo (γ+/sobre flip).")
        print(f"  -> Trampolin DEBIL. Vigilar {nivel}: si el precio cae ahi antes del vto con γ−, se arma.")
    else:
        print(f"  Sin setup de trampolin ahora (vto lejos o sin venta del MM). Revisar cerca del OPEX.")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
