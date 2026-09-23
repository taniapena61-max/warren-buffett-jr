# -*- coding: utf-8 -*-
"""
REGIMEN DE FLUJO (síntesis Roos+MS, 22-sep) — el flujo = sesgo de CONVICCION institucional.
CONFIRMA/contexto, NO es hedging (Roos) NI el nucleo ($Value/VS3D). No lidera; confirma.

Lee el flujo de MarketSnack (/api/flow), agrega compra/venta de calls vs puts (filtrando LEAPs
lejanos que ensucian), y clasifica el regimen: CALLS(alcista) / PUTS(bajista) / MIXTO.
Escribe historial/flujo_regimen.json para que selector_metodo lo lea rapido.

Uso: py scripts/flujo_regimen.py [SYM]   (default SPX). El feed es lento (~30s).
"""
import sys, json, urllib.request
from pathlib import Path
from datetime import date

SYM = (sys.argv[1] if len(sys.argv) > 1 else "SPX").upper()
BASE = "http://127.0.0.1:3000"
REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "historial" / "flujo_regimen.json"
DTE_MAX = 120   # ignorar LEAPs lejanos (ruido para el sesgo direccional del dia)


def flujo():
    try:
        req = urllib.request.urlopen(BASE + f"/api/flow?ticker={SYM}", timeout=45)
    except Exception:
        return None
    final = None
    for raw in req:
        line = raw.decode("utf-8", "ignore").strip()
        if line.startswith("data:"):
            try:
                o = json.loads(line[5:].strip())
            except Exception:
                continue
            if o.get("type") != "step":
                final = o
    return final


def main():
    f = flujo()
    if not f:
        print("[flujo_regimen] MS flow no respondio (cookie/keepalive?)."); return 1
    rows = f.get("convictionRows") or f.get("rows") or []
    bull = bear = 0.0
    n = 0
    for r in rows:
        dte = r.get("dte")
        if isinstance(dte, (int, float)) and dte > DTE_MAX:
            continue
        typ = str(r.get("type", "")).lower()
        side = str(r.get("side", "")).upper()
        prem = float(r.get("premium") or 0)
        if not typ or not side or prem <= 0:
            continue
        n += 1
        buy = "ASK" in side
        if typ == "call":
            bull += prem if buy else 0; bear += 0 if buy else prem
        elif typ == "put":
            bear += prem if buy else 0; bull += 0 if buy else prem
    tot = bull + bear
    if tot <= 0:
        reg, pct = "MIXTO", 0
    else:
        pct = 100 * abs(bull - bear) / tot
        if bull > bear and pct >= 20:
            reg = "CALLS (alcista)"
        elif bear > bull and pct >= 20:
            reg = "PUTS (bajista)"
        else:
            reg = "MIXTO"
    out = {"symbol": SYM, "date": date.today().isoformat(), "regime": reg,
           "bull_prem": round(bull), "bear_prem": round(bear), "sesgo_pct": round(pct),
           "n_rows": n}
    try:
        d = {}
        if CACHE.exists():
            d = json.loads(CACHE.read_text(encoding="utf-8"))
        d[SYM] = out
        CACHE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    print("=" * 60)
    print(f"REGIMEN DE FLUJO — {SYM} (CONFIRMA, no lidera; no es hedging ni nucleo)")
    print(f"  {reg}  | bull ${bull/1e6:.0f}M vs bear ${bear/1e6:.0f}M | sesgo {pct:.0f}% | filas {n}")
    if reg == "PUTS (bajista)":
        print("  -> MS: sin call buying agresivo = NO comprar calls. Sesgo bajista de conviccion.")
    elif reg == "CALLS (alcista)":
        print("  -> MS: entra call buying + put selling = se habilita el upside (confirmacion).")
    else:
        print("  -> mixto: sin sesgo de conviccion claro. El nucleo (VS3D/$Value) manda.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
