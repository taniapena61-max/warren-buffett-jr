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
                     min_fuentes: int = 2) -> dict:
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

    # clasificar
    resultado = []
    for z in zonas:
        n = len(z.fuentes)
        if n < min_fuentes:
            continue
        # apto para ENTRAR: confluencia suficiente Y volumen presente. Sin
        # volumen, jamás. La regla no es negociable.
        apto = (n >= min_fuentes) and volumen_confirmado
        resultado.append({
            "zona": round(z.centro, 2),
            "distancia": round(z.centro - precio, 1),
            "fuentes": sorted(z.fuentes),
            "n_fuentes": n,
            "gann_cardinal": z.gann_cardinal,
            "detalle": z.detalle,
            "volumen": "PRESENTE" if volumen_confirmado else "AUSENTE",
            "veredicto": ("ZONA DE ENTRADA (confluencia + volumen)" if apto
                          else "SOLO VIGILAR — " +
                          ("falta volumen" if not volumen_confirmado
                           else "falta confluencia")),
        })
    # ordenar: más fuentes primero, Cardinal primero, más cerca primero
    resultado.sort(key=lambda r: (-r["n_fuentes"], not r["gann_cardinal"],
                                  abs(r["distancia"])))
    return {
        "precio": precio,
        "volumen_confirmado": volumen_confirmado,
        "regla": "SIN VOLUMEN NO HAY ENTRADA. La confluencia marca la zona; "
                 "el volumen confirma que es real. Es regla de Tania, no opcional.",
        "zonas": resultado,
    }
