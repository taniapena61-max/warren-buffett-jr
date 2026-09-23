# -*- coding: utf-8 -*-
"""
DETECTOR DEL "FLIP LEVEL" del hedging del MM (Daniel Roos, creador VS3D).
El rebote/fondo de alta prob = donde el MM pasa de VENDER a COMPRAR futuros.
El techo/rechazo = donde pasa de COMPRAR a VENDER.

Confluencia de nuestros lentes:
  ABAJO (rebote / cubrir bajista / comprar):
    gamma flip (Tito) + put wall + soporte VS3D ($Value+) + Gann Cardinal
  ARRIBA (rechazo / tomar ganancia / vender):
    call wall + resistencia VS3D ($Value-) + Gann Cardinal

Uso: py scripts/flip_level.py [SYMBOL]   (default SPX)
Solo informa. No ejecuta.
"""
import sys, json, math, urllib.request
from pathlib import Path
from datetime import date

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"
REPO = Path(__file__).resolve().parent.parent
CONO_STORE = REPO / "historial" / "cono_sim.json"


def getj(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=15) as r:
            return json.load(r)
    except Exception:
        return {}


def cono_local(sym):
    """Cono/simulacion (maestra) de HOY, guardado localmente por Claude cuando
    Tania comparte los Greek Profiles. Tito descarta el campo, por eso vive aqui."""
    try:
        d = json.loads(CONO_STORE.read_text(encoding="utf-8"))
        e = d.get(sym.upper()) or {}
        if e.get("date") == date.today().isoformat():
            return e.get("cono")
    except Exception:
        return None
    return None


def gann_levels(pivot, lo, hi):
    """Niveles Gann Sq9 dentro de [lo,hi]; par=Cardinal, impar=Diagonal."""
    if not pivot or pivot <= 0:
        return []
    base = math.sqrt(pivot)
    out = []
    for k in range(-40, 41):
        lvl = (base + 0.125 * k) ** 2
        if lo <= lvl <= hi:
            out.append((round(lvl), "Cardinal" if k % 2 == 0 else "Diagonal"))
    return out


def nearest_gann(level, ganns, tol=9):
    best = None
    for lvl, tipo in ganns:
        d = abs(lvl - level)
        if d <= tol and (best is None or d < best[2]):
            best = (lvl, tipo, d)
    return best


def cluster(cands, tol=12):
    """Agrupa niveles cercanos; devuelve (centro, [fuentes]) ordenado por # fuentes."""
    cands = [c for c in cands if isinstance(c[0], (int, float)) and c[0] > 0]
    used = [False] * len(cands)
    groups = []
    for i, (lvl, src) in enumerate(cands):
        if used[i]:
            continue
        grp = [(lvl, src)]
        used[i] = True
        for j in range(i + 1, len(cands)):
            if not used[j] and abs(cands[j][0] - lvl) <= tol:
                grp.append(cands[j]); used[j] = True
        center = round(sum(x[0] for x in grp) / len(grp))
        srcs = [x[1] for x in grp]
        groups.append((center, srcs))
    groups.sort(key=lambda g: -len(g[1]))
    return groups


def main():
    a = getj(f"/api/odte?symbol={SYM}").get("analysis", {})
    spot = a.get("spot")
    if not spot:
        print(f"[flip_level] sin spot para {SYM} (¿Tito abajo?)"); return 1
    spot = float(spot)
    flip = a.get("flip"); putw = a.get("putWall"); callw = a.get("callWall")
    maxpain = a.get("maxPain"); magnet = a.get("magnet"); regime = a.get("regime")
    ng = a.get("totalNetGex")
    vsraw = getj(f"/api/vs3d-levels?symbol={SYM}")
    vs = vsraw.get("vs3d") or {}
    vs_fresh = bool(vsraw.get("fresh"))
    vs_date = vs.get("date", "?")
    sup = [float(x) for x in (vs.get("support") or []) if x]
    res = [float(x) for x in (vs.get("resistance") or []) if x]
    pivot = maxpain or magnet or round(spot / 25) * 25
    ganns = gann_levels(pivot, spot - 250, spot + 250)

    # candidatos ABAJO (rebote) = flip, putWall, soportes VS3D bajo el spot
    down = []
    if isinstance(flip, (int, float)) and flip < spot: down.append((round(flip), "gammaFlip"))
    if isinstance(putw, (int, float)) and putw <= spot: down.append((round(putw), "putWall"))
    for s in sup:
        if s < spot: down.append((round(s), "VS3D-sop"))
    # candidatos ARRIBA (rechazo) = callWall, resistencias VS3D sobre el spot
    up = []
    if isinstance(callw, (int, float)) and callw >= spot: up.append((round(callw), "callWall"))
    for r in res:
        if r > spot: up.append((round(r), "VS3D-res"))

    print("=" * 66)
    print(f"FLIP LEVEL DETECTOR — {SYM}  spot {spot:.1f} | regimen {regime} | netGEX {round((ng or 0)/1e9,1)}B")
    print(f"  (pivote Gann {pivot}, maxpain {maxpain}, magnet {magnet})")
    if not vs_fresh:
        print(f"  [!] OJO: VS3D NO es de hoy (fecha {vs_date}) -> los niveles VS3D pueden estar viejos.")
        print(f"      Pide a Tania el VS3D fresco y re-corre. Gamma-flip/put-call wall SÍ son de hoy.")
    else:
        print(f"  [OK] VS3D fresco ({vs_date}).")
    print("=" * 66)

    # DESTINO — FOTO ($Value/pin) vs SIMULACION (cono maestra).  Regla Roos:
    # "SIMULACION, no foto" -> si difieren, MANDA el cono. El cono no tiene feed;
    # Claude lo registra al POST vs3d-levels (campo "cono") cuando Tania comparte
    # la maestra (Greek Profiles). Ver memoria simulacion-cono-manda-sobre-value-foto.
    foto = a.get("pin") or magnet or maxpain
    cono = vs.get("cono") or cono_local(SYM)
    print("\nDESTINO — FOTO vs SIMULACION (Roos: si difieren, manda la SIMULACION):")
    if cono is None:
        print(f"  foto (pin/$Value): {foto}   |   simulacion (cono): NO CARGADA")
        print(f"  [!] Pedir la maestra a Tania y registrar el cono (POST /api/vs3d-levels campo \"cono\").")
        print(f"      Sin el cono NO decidir el destino solo con la foto (ese fue el error 22-sep).")
    else:
        try:
            d = abs(float(cono) - float(foto))
        except (TypeError, ValueError):
            d = None
        print(f"  foto (pin/$Value): {foto}   |   simulacion (cono): {cono}"
              + (f"   |   dif {d:.0f}pt" if d is not None else ""))
        if d is not None and d >= 10:
            print(f"  -> DIVIDIDO (dif>=10): LIDERAR el cono {cono}. Dar entradas ARRIBA y ABAJO, que Tania elija.")
        else:
            print(f"  -> foto y simulacion COINCIDEN (~{cono}): destino confiable.")
    print("=" * 66)

    def show(title, groups, side):
        print(f"\n{title}")
        if not groups:
            print("  (sin candidatos)"); return
        for center, srcs in groups[:3]:
            g = nearest_gann(center, ganns)
            gtxt = f" +Gann {g[1]} {g[0]}" if g else ""
            conf = len(set(srcs)) + (1 if g else 0)
            dist = center - spot
            estrellas = "***" if conf >= 3 else ("**" if conf == 2 else "*")
            print(f"  {estrellas} {center}  ({dist:+.0f} pts)  <- {', '.join(sorted(set(srcs)))}{gtxt}  [confluencia {conf}]")

    show("REBOTE / cubrir bajista / comprar (abajo — MM pasa a COMPRAR):", cluster(down), "down")
    show("RECHAZO / tomar ganancia / vender (arriba — MM pasa a VENDER):", cluster(up), "up")
    print("\nLectura: el nivel con MÁS confluencia (***) es el flip mecánico de mayor prob.")
    print("Rebote = entrar/ cubrir bajista ahí. Rechazo = tomar ganancia / vender ahí. Esperar toque+giro, no perseguir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
