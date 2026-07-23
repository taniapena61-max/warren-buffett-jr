"""Almacén de historial diario — guarda lo que Schwab no guarda.

Schwab entrega la foto de HOY pero no conserva el pasado. Este módulo va
apilando cada consulta en un CSV por símbolo, una fila por día (la última
consulta del día pisa a las anteriores), para que con el tiempo tengamos algo
que Schwab no puede dar: la evolución diaria de precios, IV, delta, etc.

- No se puede ir hacia atrás (los días previos a hoy están perdidos), pero
  desde el primer registro en adelante la serie es nuestra.
- Idempotente por fecha: correr el monitor 20 veces en un día deja UNA fila.
- Defensivo: si el guardado falla, nunca rompe a quien llama.
- Los datos viven en `historial/` (personal, ignorado por git).

Uso típico (desde el monitor o el proveedor):
    from wbj.history import registrar
    registrar("IREN", {"precio": 41.29, "iv": 130.5}, repo_root)
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

# Campos que interesan de una cotización de Schwab, con nombre estable.
_CAMPOS_OPCION = {
    "mark": "mark", "lastPrice": "last", "bidPrice": "bid", "askPrice": "ask",
    "delta": "delta", "gamma": "gamma", "theta": "theta", "vega": "vega",
    "volatility": "iv", "openInterest": "oi", "totalVolume": "volumen",
    "timeValue": "valor_temporal", "underlyingPrice": "subyacente",
    "closePrice": "cierre_previo",
}


def _carpeta(base: Path) -> Path:
    """Acepta tanto el repo_root como la propia carpeta 'historial'.

    Asi da igual pasar `repo_root` o `repo_root/historial`: nunca se duplica
    en 'historial/historial'.
    """
    d = base if base.name == "historial" else base / "historial"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _archivo(base: Path, simbolo: str) -> Path:
    # nombre seguro: los símbolos de opción llevan espacios
    slug = simbolo.strip().replace(" ", "_").replace("/", "_")
    return _carpeta(base) / f"{slug}.csv"


def registrar(simbolo: str, campos: dict, repo_root: Path,
              cuando: date | None = None) -> bool:
    """Añade/actualiza la fila del día para `simbolo`. True si guardó.

    Upsert por fecha: si ya hay fila de hoy, se reemplaza con los datos más
    recientes (la última consulta del día es la que queda). Nunca lanza.
    """
    try:
        dia = (cuando or date.today()).isoformat()
        fila = {"fecha": dia}
        for k, v in campos.items():
            if isinstance(v, (int, float)):
                fila[k] = round(float(v), 4)
            elif v is not None:
                fila[k] = v

        path = _archivo(repo_root, simbolo)
        filas: list[dict] = []
        columnas: list[str] = ["fecha"]
        if path.exists():
            with path.open("r", encoding="utf-8", newline="") as fh:
                r = csv.DictReader(fh)
                columnas = r.fieldnames or ["fecha"]
                filas = [row for row in r if row.get("fecha") != dia]  # quita hoy

        # unir columnas nuevas conservando orden
        for c in fila:
            if c not in columnas:
                columnas.append(c)
        filas.append({c: fila.get(c, "") for c in columnas})
        filas.sort(key=lambda x: x.get("fecha", ""))

        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=columnas)
            w.writeheader()
            for row in filas:
                w.writerow({c: row.get(c, "") for c in columnas})
        return True
    except (OSError, ValueError, csv.Error):
        return False


def registrar_quote(simbolo: str, quote: dict, repo_root: Path) -> bool:
    """Extrae los campos útiles de una cotización Schwab y los guarda."""
    if not isinstance(quote, dict):
        return False
    campos = {nom: quote[k] for k, nom in _CAMPOS_OPCION.items()
              if quote.get(k) is not None}
    if not campos:
        return False
    return registrar(simbolo, campos, repo_root)


def leer(simbolo: str, repo_root: Path) -> list[dict]:
    """Devuelve toda la serie histórica de un símbolo (lista de filas)."""
    path = _archivo(repo_root, simbolo)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))
    except (OSError, csv.Error):
        return []
