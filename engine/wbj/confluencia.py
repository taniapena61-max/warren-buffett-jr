"""Mapa de correlación de strikes — la confluencia de Tania.

Cruza TRES lentes independientes para encontrar zonas de alta convicción:
  1. Gann (Square of 9)  — geometría de precio-tiempo (se calcula aquí).
  2. VS3D                — posición de los market makers (strikes que aporta Tania).
  3. MarketSnack         — dónde están las grandes instituciones (idem).

Y una REGLA INQUEBRANTABLE de Tania: **ninguna zona es apta para entrar sin
VOLUMEN presente confirmando el nivel.** El volumen es el juez final. La
confluencia dice DÓNDE mirar; el volumen dice si el nivel es real. Sin volumen =
falso movimiento (clase de VS3D / Wyckoff esfuerzo-vs-resultado).

Por eso `mapa_confluencia` NUNCA marca una zona como "ENTRADA" a menos que
`volumen_confirmado=True`. Es a propósito: el código no deja saltarse la regla.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Ángulos del Square of 9 (grados). Cardinal = fuerte; Diagonal = secundario.
CARDINALES = (0, 90, 180, 270)
DIAGONALES = (45, 135, 225, 315)


def gann_sq9(pivote: float, precio: float, rango: float = 0.04,
             anillos: int = 6) -> list[dict]:
    """Niveles de Gann Square of 9 alrededor de un pivote.

    Fórmula (calibrada con la hoja de Tania): nivel = (√pivote ± inc)²,
    con inc = anillo + ángulo/360. Alcistas suman, bajistas restan.
    Devuelve solo los niveles dentro de ±`rango` del precio actual.
    """
    raiz = math.sqrt(pivote)
    lo, hi = precio * (1 - rango), precio * (1 + rango)
    out: list[dict] = []
    for anillo in range(anillos + 1):
        for ang in CARDINALES + DIAGONALES:
            inc = anillo + ang / 360.0
            for signo, dirn in ((+1, "alcista"), (-1, "bajista")):
                nivel = (raiz + signo * inc) ** 2
                if lo <= nivel <= hi:
                    out.append({
                        "nivel": round(nivel, 2), "angulo": ang,
                        "tipo": "Cardinal" if ang in CARDINALES else "Diagonal",
                        "direccion": dirn, "anillo": anillo,
                    })
    # dedup por nivel redondeado, priorizando Cardinal
    vistos: dict[float, dict] = {}
    for r in sorted(out, key=lambda x: (x["nivel"], x["tipo"] != "Cardinal")):
        vistos.setdefault(r["nivel"], r)
    return sorted(vistos.values(), key=lambda x: x["nivel"])


def evaluar_vix(vix_nivel: float | None = None,
                backwardation: bool = False,
                subiendo_spx_plano: bool = False) -> dict:
    """Filtro de régimen del VIX para confirmar una entrada de venta de prima.

    De la clase del VIX + Vanna: el VIX confirma o VETA según el régimen.
      - backwardation (curva invertida) -> el régimen cambió: NO vender prima.
      - VIX subiendo con SPX plano -> venta mecánica en camino: aviso serio.
      - contango + VIX estable -> viento a favor del vendedor de prima.
    Devuelve {"estado": favorable|precaucion|veta, "razon": ...}.
    """
    if backwardation:
        return {"estado": "veta",
                "razon": "curva en BACKWARDATION — el régimen cambió, no vender prima"}
    if subiendo_spx_plano:
        return {"estado": "veta",
                "razon": "VIX subiendo con SPX plano — venta mecánica en camino"}
    if vix_nivel is not None and vix_nivel < 12:
        return {"estado": "precaucion",
                "razon": f"VIX {vix_nivel:.1f} muy bajo (complacencia) — poco colchón, la vol solo puede subir"}
    return {"estado": "favorable",
            "razon": "contango / VIX estable — viento a favor del vendedor de prima"}


@dataclass
class Zona:
    centro: float
    niveles: list[float] = field(default_factory=list)
    fuentes: set[str] = field(default_factory=set)
    gann_cardinal: bool = False
    detalle: list[str] = field(default_factory=list)


def mapa_confluencia(precio: float, gann: list[dict],
                     vs3d: list[float] | None = None,
                     marketsnack: list[float] | None = None,
                     tolerancia: float = 5.0,
                     volumen_confirmado: bool = False,
                     min_fuentes: int = 2,
                     vix: dict | None = None) -> dict:
    """Agrupa niveles de las 3 fuentes en zonas de confluencia.

    - `tolerancia`: pts para considerar que dos niveles son la misma zona.
    - `min_fuentes`: cuántas de las 3 lentes deben coincidir para que cuente.
    - `volumen_confirmado`: la REGLA DE TANIA. Si es False, NINGUNA zona sale
      como apta para entrar, por más confluencia que haya.

    Devuelve zonas ordenadas por fuerza (nº de fuentes, Cardinal primero).
    """
    puntos: list[tuple[float, str, str]] = []
    for g in gann:
        etq = f"Gann {g['angulo']}° {g['tipo']} ({g['direccion']})"
        puntos.append((g["nivel"], "Gann", etq + (" ★" if g["tipo"] == "Cardinal" else "")))
    for s in (vs3d or []):
        puntos.append((float(s), "VS3D", f"VS3D {s:.0f}"))
    for s in (marketsnack or []):
        puntos.append((float(s), "MarketSnack", f"MarketSnack {s:.0f}"))

    puntos.sort(key=lambda p: p[0])
    zonas: list[Zona] = []
    for nivel, fuente, etq in puntos:
        z = next((z for z in zonas if abs(z.centro - nivel) <= tolerancia), None)
        if z is None:
            z = Zona(centro=nivel)
            zonas.append(z)
        z.niveles.append(nivel)
        z.fuentes.add(fuente)
        z.detalle.append(etq)
        if fuente == "Gann" and "★" in etq:
            z.gann_cardinal = True
        z.centro = round(sum(z.niveles) / len(z.niveles), 2)  # centro = media

    # filtro VIX (tercera luz). Si no se pasa, no se evalúa (no veta).
    vix = vix or {"estado": "no_evaluado", "razon": "VIX no aportado"}
    vix_veta = vix["estado"] == "veta"
    vix_ok = vix["estado"] in ("favorable", "no_evaluado")

    # clasificar
    resultado = []
    for z in zonas:
        n = len(z.fuentes)
        if n < min_fuentes:
            continue
        # Las TRES luces para ENTRAR: confluencia + volumen + VIX no en contra.
        luz_conf = n >= min_fuentes
        luz_vol = volumen_confirmado
        luz_vix = not vix_veta
        apto = luz_conf and luz_vol and luz_vix
        faltan = []
        if not luz_vol:
            faltan.append("VOLUMEN")
        if vix_veta:
            faltan.append("VIX en contra")
        resultado.append({
            "zona": round(z.centro, 2),
            "distancia": round(z.centro - precio, 1),
            "fuentes": sorted(z.fuentes),
            "n_fuentes": n,
            "gann_cardinal": z.gann_cardinal,
            "detalle": z.detalle,
            "luces": {"confluencia": luz_conf, "volumen": luz_vol,
                      "vix": vix_ok},
            "volumen": "PRESENTE" if volumen_confirmado else "AUSENTE",
            "vix": vix["razon"],
            "veredicto": ("ZONA DE ENTRADA (confluencia + volumen + VIX)" if apto
                          else "SOLO VIGILAR — falta: " + ", ".join(faltan)),
        })
    # ordenar: más fuentes primero, Cardinal primero, más cerca primero
    resultado.sort(key=lambda r: (-r["n_fuentes"], not r["gann_cardinal"],
                                  abs(r["distancia"])))
    return {
        "precio": precio,
        "volumen_confirmado": volumen_confirmado,
        "vix": vix,
        "regla": "TRES LUCES PARA ENTRAR: (1) confluencia de las 3 lentes, "
                 "(2) VOLUMEN presente, (3) VIX no en contra. Sin volumen NUNCA "
                 "se entra; el VIX en backwardation o subiendo con SPX plano veta. "
                 "Regla de Tania, no opcional.",
        "zonas": resultado,
    }
