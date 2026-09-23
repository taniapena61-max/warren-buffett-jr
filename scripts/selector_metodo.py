# -*- coding: utf-8 -*-
"""
SELECTOR DE MÉTODO DEL DÍA — condición del mercado -> método que GANA -> entrada.
Nace de la regla de Tania (21-sep): "sin trades no existimos". Los filtros ELIGEN
el método, NUNCA bloquean. SIEMPRE sale >=1 setup ejecutable con gatillo.

Corre en el arranque (buenos días) y se puede re-correr en cambios de régimen.
Uso: py scripts/selector_metodo.py [SYM]   (default SPX)
Solo informa; Tania decide y ejecuta en su broker.
"""
import sys, json, subprocess, os, urllib.request
from datetime import datetime
from pathlib import Path

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"
REPO = Path(r"C:\Users\tania\Desktop\warren-buffett-jr")


def getj(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=15) as r:
            return json.load(r)
    except Exception:
        return {}


def cono_local(sym):
    """Cono/simulacion (maestra Greek Profiles) de HOY. Regla Roos: la SIMULACION
    manda sobre la foto ($Value/pin). Claude lo escribe al compartir la maestra.
    Tito descarta el campo, por eso vive en historial/cono_sim.json."""
    from datetime import date
    try:
        d = json.loads((REPO / "historial" / "cono_sim.json").read_text(encoding="utf-8"))
        e = d.get(sym.upper()) or {}
        if e.get("date") == date.today().isoformat():
            return e.get("cono")
    except Exception:
        return None
    return None


def flujo_regimen(sym):
    """Regimen de flujo de HOY (calls vs puts) = sesgo de CONVICCION (sintesis Roos+MS):
    confirma, NO lidera, NO es hedging ni nucleo. Lo escribe flujo_regimen.py."""
    from datetime import date
    try:
        d = json.loads((REPO / "historial" / "flujo_regimen.json").read_text(encoding="utf-8"))
        e = d.get(sym.upper()) or {}
        if e.get("date") == date.today().isoformat():
            return e
    except Exception:
        return None
    return None


def vix_now():
    d = getj(f"/api/salud?symbol={SYM}")
    for l in d.get("lentes", []):
        if l.get("lente") == "VIX / volatilidad":
            det = l.get("detalle", "")
            try:
                return float(det.split("VIX")[1].split("·")[0].strip())
            except Exception:
                return None
    return None


def trend_hoy():
    """up/down/no desde pin_intradia (spots de HOY). Pre-open -> 'no'."""
    src = REPO / "historial" / "pin_intradia.jsonl"
    hoy = datetime.now().strftime("%Y-%m-%d")
    spots = []
    if src.exists():
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if str(d.get("ts", "")).startswith(hoy) and isinstance(d.get("spot"), (int, float)):
                spots.append(float(d["spot"]))
    spots = spots[-4:]
    if len(spots) < 4:
        return "no", spots
    difs = [spots[i+1]-spots[i] for i in range(len(spots)-1)]
    neto = spots[-1]-spots[0]
    if all(x >= -1 for x in difs) and neto > 12:
        return "up", spots
    if all(x <= 1 for x in difs) and neto < -12:
        return "down", spots
    return "no", spots


def flip_levels():
    try:
        out = subprocess.run([sys.executable, str(REPO/"scripts"/"flip_level.py"), SYM],
                             capture_output=True, text=True, timeout=35,
                             encoding="utf-8", errors="replace").stdout or ""
        reb = rej = None
        sec = None
        for l in out.splitlines():
            if "REBOTE" in l: sec = "reb"
            elif "RECHAZO" in l: sec = "rej"
            elif sec and "pts)" in l:
                lvl = l.strip().split()[1]
                if sec == "reb" and reb is None: reb = lvl
                if sec == "rej" and rej is None: rej = lvl
        return reb, rej
    except Exception:
        return None, None


def main():
    a = getj(f"/api/odte?symbol={SYM}").get("analysis", {})
    spot = a.get("spot")
    if not spot:
        print("[selector] sin spot (¿Tito abajo? renovar Schwab / reiniciar Tito)."); return 1
    spot = float(spot)
    reg = str(a.get("regime", "")).lower()
    ng = (a.get("totalNetGex") or 0) / 1e9
    pin = a.get("pin"); magnet = a.get("magnet"); callw = a.get("callWall"); putw = a.get("putWall")
    maxpain = a.get("maxPain"); mtc = a.get("minutesToClose"); mopen = a.get("marketOpen")
    vix = vix_now()
    tr, spots = trend_hoy()
    reb, rej = flip_levels()
    dist_pin = abs(spot - pin) if isinstance(pin, (int, float)) else None
    hh = datetime.now().hour + datetime.now().minute/60.0
    # DESTINO: simulacion (cono) manda sobre foto (pin) si difieren >=10pt (Roos).
    cono = cono_local(SYM)
    cuerpo = pin
    cono_split = False
    if isinstance(cono, (int, float)) and isinstance(pin, (int, float)) and abs(cono - pin) >= 10:
        cuerpo = cono; cono_split = True

    gpos = ng >= 4
    gneg = ng < 0
    print("=" * 68)
    print(f"SELECTOR DE MÉTODO DEL DÍA — {SYM}  {datetime.now():%H:%M}")
    print("=" * 68)
    print(f"Condición: spot {spot:.1f} | regimen {reg} ({ng:+.1f}B) | VIX {vix} | "
          f"tendencia {tr} | pin {pin} (dist {dist_pin}) | mktOpen {mopen} | min_cierre {mtc}")
    print(f"Niveles clave: rebote(flip) {reb} · rechazo(flip) {rej} · pin {pin} · "
          f"callWall {callw} · putWall {putw} · maxpain {maxpain}")
    if cono_split:
        print(f"** DESTINO DIVIDIDO (Roos): foto(pin) {pin} vs simulacion(cono) {cono} -> "
              f"LIDERA el CONO {cono}. Cuerpo del fly = {cuerpo}. Dar entradas ARRIBA y ABAJO.")
    elif isinstance(cono, (int, float)):
        print(f"   destino: foto(pin) {pin} y cono {cono} COINCIDEN -> cuerpo {cuerpo} confiable.")
    else:
        print(f"   [!] cono/simulacion NO cargado -> pedir la maestra a Tania y registrar el cono "
              f"antes de fijar el cuerpo (no decidir solo con la foto).")
    # Reglas Roos operativas (sin feed propio -> disciplina):
    if isinstance(mtc, (int, float)) and 0 <= mtc <= 150:
        print("   [Roos #8] CHARM sesgo casi siempre ARRIBA: si el settle esta indeciso entre "
              "dos destinos cercanos, INCLINA al de arriba (charm compra en la tarde).")
    # #9 SINTESIS Roos+MS (Tania 22-sep): flujo = sesgo de CONVICCION -> CONFIRMA, no lidera;
    # no es hedging (Roos) ni el nucleo ($Value/VS3D). El nucleo manda; el flujo confirma.
    fr = flujo_regimen(SYM)
    if fr:
        print(f"   [Flujo #9] REGIMEN {fr.get('regime')} (bull ${fr.get('bull_prem',0)/1e6:.0f}M vs "
              f"bear ${fr.get('bear_prem',0)/1e6:.0f}M, sesgo {fr.get('sesgo_pct')}%) = "
              f"CONVICCION que CONFIRMA. No lidera, no es hedging ni nucleo.")
    else:
        print("   [Flujo #9] regimen de flujo no cargado -> correr flujo_regimen.py. "
              "Recordatorio: flujo = conviccion que CONFIRMA (no lidera, no hedging, no nucleo).")
    print("-" * 68)

    setups = []
    # 1) APERTURA (delta) 9:30-9:45
    if mopen and 9.5 <= hh <= 9.8:
        setups.append(("DELTA APERTURA (Tarjeta 1)",
                       "Vender ITM ~delta .70, salir .30/.35. gamma+ mariposa / gamma- vertical. Ventana 9:30-9:45."))
    # 2) TENDENCIA -> direccional / vertical al rechazo (NUNCA fly de pin)
    if tr == "up":
        setups.append(("DIRECCIONAL ALCISTA / vertical al rechazo",
                       f"NO fly de pin (tendencia). Montar: call debit spread a favor hacia {rej or callw}. "
                       f"O vender bear-call vertical SOLO si toca {rej or callw} y RECHAZA (giro)."))
    elif tr == "down":
        setups.append(("DIRECCIONAL BAJISTA / vertical al rechazo",
                       f"NO fly de pin. Put debit spread a favor hacia {reb or putw}. "
                       f"O bull-put vertical si toca {reb or putw} y GIRA (rebote/flip)."))
    # 3) REBOTE al flip (entrada de alta prob)
    if reb and dist_pin is not None:
        setups.append(("ENTRADA REBOTE en el FLIP (toque+giro)",
                       f"Si el precio CAE al flip {reb} (rebote mecánico del MM) y gira -> entrar "
                       f"(spread alcista / fly en el rebote). Es tu mejor entrada de alta prob."))
    # 4) PIN FLY -> solo gamma+ estable, spot cerca, sin tendencia
    if gpos and tr == "no" and dist_pin is not None and dist_pin <= 15:
        setups.append(("FLY DE PIN (Tarjeta 2)",
                       f"gamma+ + pin estable + spot a {dist_pin:.0f}pt (<15 = fade fiable ~100% en tu backtest). "
                       f"Cuerpo {cuerpo}"
                       + (f" (=CONO, no el pin {pin} — Roos manda la simulacion)" if cono_split else "")
                       + ", alas ±15. Post-11h ideal. Correr pin_estable antes."))
    elif gpos and tr == "no" and dist_pin is not None and dist_pin > 15:
        setups.append(("FLY DE PIN — ESPERAR estiramiento/giro",
                       f"gamma+ pero spot a {dist_pin:.0f}pt del pin (estirado). Esperar toque+giro a la banda "
                       f"o que se acerque <15pt. NO vender pegada al borde."))
    # 5) gamma NEGATIVA -> direccional camino de menor resistencia
    if gneg:
        setups.append(("DIRECCIONAL (gamma-)",
                       f"gamma- = movimientos violentos, sin contención. Operar A FAVOR del camino "
                       f"(flip {rej if tr!='down' else reb}). NO vender prima (flies revientan)."))
    # 6) CIERRE post-2PM
    if mopen and hh >= 14.0:
        setups.append(("CIERRE / resolver el precio (post-2PM)",
                       f"Fly en el settle: cuerpo maxpain(gamma+)/charm(gamma-) ~{maxpain or pin}. "
                       f"El estrade debe ir a 0."))

    if not setups:
        # nunca 'no hay trade' seco: dar el gatillo
        setups.append(("GATILLO (sin setup inmediato limpio)",
                       f"Espera: (a) toque del flip {reb} para entrada de rebote, o "
                       f"(b) pin estable + spot <15pt para el fly. Te aviso cuando dispare."))

    print("MÉTODO(S) DEL DÍA — EJECUTABLES:")
    for i, (name, desc) in enumerate(setups, 1):
        print(f"  {i}) {name}\n     -> {desc}")
    print("-" * 68)
    print("REGLA: el filtro ELIGE el método, no bloquea. Si el A no encaja, se PIVOTA. SIEMPRE hay trade.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
