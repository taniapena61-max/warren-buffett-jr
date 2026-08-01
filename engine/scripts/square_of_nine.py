"""Calculadora Square of Nine (Gann) + buscador de confluencias.

Metodo de Tania:
  nivel_alcista = (sqrt(pivote) + anillo + angulo/360)^2
  nivel_bajista = (sqrt(pivote) - anillo - angulo/360)^2

El pivote se toma del CUERPO de la vela del minimo/maximo mayor (criterio fijo
de Tania, decidido 2026-07-24), NO de la mecha.

Su senal de alta probabilidad es cuando coinciden LAS TRES herramientas en un
mismo strike: VS3D (imanes del market maker) + MarketSnack (flujo) + Square of
Nine. Este script cruza las tres y devuelve solo las coincidencias.

SOLO LECTURA: consulta el precio en Schwab, no toca ordenes ni posiciones.

Uso:
    python scripts/square_of_nine.py                 # pivote y niveles por defecto
    python scripts/square_of_nine.py 6317            # otro pivote
    python scripts/square_of_nine.py 6317 --tol 12   # tolerancia de confluencia
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Configuracion editable ------------------------------------------------

PIVOTE_DEFECTO = 6317.0   # cuerpo del minimo mayor del SPX (grafico diario)
SIMBOLO = "$SPX"

# Imanes / muros leidos del VS3D. Editar tras cada lectura nueva.
# 2026-07-28 (9:28 AM, spot 7423.74): muro ROJO 7430, green 7460/7410/7350/7300,
# bandas straddle 7459.06 (+35.30) / 7388.44 (-35.30).
NIVELES_VS3D = [7300, 7350, 7388, 7410, 7430, 7459]

# Niveles de la grafica de TradingView (lineas moradas, negras, POC).
NIVELES_GRAFICA = [6822.56, 7008.09, 7210.31, 7239.74, 7319.97, 7470.87, 7484.86, 7495.90]

# Strikes donde el flujo de MarketSnack mostro tamano relevante.
NIVELES_FLUJO = [7300, 7350, 7450, 7500]

ANGULOS = [
    (0,   "E",  "Cardinal", "Expansion"),
    (45,  "NE", "Diagonal", "Expansion"),
    (90,  "N",  "Cardinal", "Consolidacion"),
    (135, "NO", "Diagonal", "Consolidacion"),
    (180, "O",  "Cardinal", "Contraccion"),
    (225, "SO", "Diagonal", "Contraccion"),
    (270, "S",  "Cardinal", "Reversion"),
    (315, "SE", "Diagonal", "Reversion"),
]


def niveles(pivote: float, anillos: int = 12, alcista: bool = True) -> list[dict]:
    """Genera la rejilla Square of Nine desde `pivote`."""
    raiz = math.sqrt(pivote)
    salida = []
    for anillo in range(anillos):
        for ang, direccion, tipo, fase in ANGULOS:
            inc = anillo + ang / 360.0
            base = raiz + inc if alcista else raiz - inc
            if base <= 0:
                continue
            salida.append({
                "nivel": round(base ** 2),
                "anillo": anillo + 1,
                "angulo": ang,
                "dir": direccion,
                "tipo": tipo,
                "fase": fase,
            })
    return salida


def precio_vivo() -> float | None:
    """Precio del SPX desde Schwab. None si no hay token."""
    try:
        from wbj.config import load_settings
        from wbj.providers.schwab import SchwabProvider
        s = load_settings()
        sch = SchwabProvider(s.schwab_app_key, s.schwab_app_secret,
                             s.schwab_callback_url, s.schwab_token_path)
        return sch.last_price(SIMBOLO)
    except Exception:  # noqa: BLE001 - el script debe correr sin Schwab
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pivote", nargs="?", type=float, default=PIVOTE_DEFECTO)
    ap.add_argument("--precio", type=float, default=None)
    ap.add_argument("--tol", type=float, default=10.0,
                    help="tolerancia en puntos para declarar confluencia")
    ap.add_argument("--rango", type=float, default=350.0,
                    help="puntos arriba/abajo del precio a mostrar")
    args = ap.parse_args()

    precio = args.precio or precio_vivo()
    if precio is None:
        print("No pude leer el precio de Schwab. Pasa uno con --precio 7408")
        sys.exit(1)

    rejilla = niveles(args.pivote)
    cerca = [n for n in rejilla if abs(n["nivel"] - precio) <= args.rango]
    cerca.sort(key=lambda n: n["nivel"])

    print("=" * 78)
    print(f"SQUARE OF NINE  |  pivote {args.pivote:,.0f} (cuerpo)  |  SPX {precio:,.2f}")
    print(f"tolerancia de confluencia: +-{args.tol:.0f} pts")
    print("=" * 78)
    print(f"{'NIVEL':>8} {'TIPO':<9} {'FASE':<14} {'AN':>3} {'ANG':>4} {'dist':>7}   CONFLUENCIA")
    print("-" * 78)

    externos = [
        ("VS3D", NIVELES_VS3D),
        ("Grafica", NIVELES_GRAFICA),
        ("Flujo", NIVELES_FLUJO),
    ]

    triples = []
    for n in cerca:
        marcas = []
        for etiqueta, lista in externos:
            hit = [x for x in lista if abs(x - n["nivel"]) <= args.tol]
            if hit:
                d = min(abs(x - n["nivel"]) for x in hit)
                marcas.append(f"{etiqueta}({d:.0f})")
        dist = n["nivel"] - precio
        estrella = ""
        if len(marcas) >= 3:
            estrella = "  *** TRIPLE ***"
            triples.append((n, marcas))
        elif len(marcas) == 2:
            estrella = "  ** doble **"
        fuerte = "*" if n["tipo"] == "Cardinal" else " "
        print(f"{n['nivel']:>8,} {n['tipo']:<8}{fuerte} {n['fase']:<14} "
              f"{n['anillo']:>3} {n['angulo']:>4} {dist:>+7.0f}   "
              f"{' '.join(marcas)}{estrella}")

    print("-" * 78)
    print("* junto al tipo = Cardinal (fuerte). Sin asterisco = Diagonal (secundario).")
    print(f"distancia media esperada al azar: ~{(rejilla[8]['nivel'] - rejilla[0]['nivel']) / 16:.0f} pts")

    if triples:
        print("\n" + "=" * 78)
        print("COINCIDENCIAS TRIPLES  (VS3D + Grafica + Flujo sobre un nivel Gann)")
        print("=" * 78)
        for n, marcas in triples:
            peso = "FUERTE (Cardinal)" if n["tipo"] == "Cardinal" else "secundaria (Diagonal)"
            print(f"  {n['nivel']:,}  {n['fase']:<14} anillo {n['anillo']} {n['angulo']}deg"
                  f"  -> {peso}")
            print(f"      {'  '.join(marcas)}")
    else:
        print("\nSin coincidencias triples en el rango. No forzar una entrada.")


if __name__ == "__main__":
    main()
