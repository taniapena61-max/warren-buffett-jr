"""Lector de MarketSnack — flujo de opciones (proveedor de datos de mercado).

MarketSnack aún no tiene API oficial; su dueño autorizó a Tania a usar la cookie
de sesión. La cookie vive SOLO en `API/.env` (gitignored), la pega Tania ella
misma; este código nunca la imprime ni la registra. Como es proveedor de datos,
no hay información personal de Tania de por medio.

La cookie de sesión **caduca en días** — cuando el feed devuelva 401/403, hay que
refrescarla (volver a copiarla del navegador), igual que se renueva Schwab.

Estado: esqueleto. Falta el ENDPOINT real (la petición `flow_feed` que devuelve
JSON) y el formato de su respuesta — Tania los aporta desde DevTools. Con eso se
completa `_parsear` para extraer los strikes que alimentan el mapa de confluencia.
"""

from __future__ import annotations

import httpx

# Endpoint real (confirmado por Tania desde DevTools, 2026-07-25).
_FLOW_URL = "https://app.marketsnack.com/api/flow_feed"
_REFERER = "https://app.marketsnack.com/app/flow-feed"


class MarketSnackProvider:
    """Cliente de solo lectura del feed de MarketSnack vía cookie de sesión."""

    def __init__(self, cookie: str | None, client: httpx.Client | None = None,
                 flow_url: str = _FLOW_URL) -> None:
        self._cookie = cookie
        self.flow_url = flow_url
        self.client = client or httpx.Client(timeout=15.0)

    @property
    def configured(self) -> bool:
        return bool(self._cookie)

    def _headers(self) -> dict:
        # La cookie se usa solo aquí, en memoria; nunca se loguea.
        return {
            "Cookie": self._cookie or "",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) warren-buffett-jr",
            "Accept": "application/json",
            "Referer": _REFERER,
            "X-Requested-With": "XMLHttpRequest",
        }

    def fetch_flow(self, symbol: str = "IREN", premium_min: int = 100000,
                   fecha: str | None = None) -> dict:
        """Baja el feed crudo. {"error": ...} si falla o la cookie caducó.

        Replica los filtros de la URL de MarketSnack (formato filter[...][...]).
        `fecha` es un día YYYY-MM-DD (por defecto hoy).
        """
        if not self._cookie:
            return {"error": "falta MARKETSNACK_COOKIE en API/.env"}
        from datetime import date as _date
        dia = fecha or _date.today().isoformat()
        # httpx codifica los corchetes; el servidor espera %5B/%5D.
        q = [
            ("filter[scope]", "all"),
            ("filter[symbol][]", symbol.upper()),
            ("filter[premium][gte]", str(premium_min)),
            ("filter[date][gte]", dia),
            ("filter[date][lte]", dia),
            ("filter[time][gte]", "0"),
            ("filter[time][lte]", "1439"),
            ("filter[delta][gte]", "0"),
            ("filter[delta][lte]", "1"),
            ("filter[asset_type][exclude][]", "ETF"),
            ("sort[field]", "premium"),
            ("sort[direction]", "desc"),
        ]
        try:
            r = self.client.get(self.flow_url, params=q, headers=self._headers())
        except httpx.HTTPError as e:
            return {"error": f"red: {type(e).__name__}"}
        if r.status_code in (401, 403):
            return {"error": "cookie caducada — refréscala desde el navegador"}
        if r.status_code != 200:
            return {"error": f"MarketSnack respondió {r.status_code}"}
        try:
            return {"data": r.json()}
        except ValueError:
            return {"error": "respuesta no es JSON (¿endpoint incorrecto?)"}

    def flujo(self, symbol: str = "IREN", premium_min: int = 100000,
              fecha: str | None = None) -> list[dict]:
        """Operaciones grandes procesadas: strike, tipo, premium, sentiment, etc.

        Devuelve la lista lista para usar (vacía si falla). Cada fila:
        {strike, tipo, vencimiento, premium, sentiment, side, delta, oi, volumen}.
        """
        r = self.fetch_flow(symbol, premium_min, fecha)
        if r.get("error"):
            return []
        return _parsear(r["data"])

    def strikes_para_confluencia(self, symbol: str = "IREN",
                                 top: int = 8) -> list[float]:
        """Los strikes de mayor premium (los que importan para la confluencia)."""
        filas = self.flujo(symbol)
        # dedup por strike, quedándose con el de mayor premium
        por_strike: dict[float, float] = {}
        for f in filas:
            por_strike[f["strike"]] = max(por_strike.get(f["strike"], 0), f["premium"])
        ordenados = sorted(por_strike.items(), key=lambda kv: kv[1], reverse=True)
        return [k for k, _ in ordenados[:top]]


def _parse_occ(sym: str) -> dict | None:
    """Descompone un símbolo OCC 'IREN260807P00034000'.

    Formato: RAÍZ + AAMMDD + C/P + strike(8 dígitos, ×1000).
    """
    import re
    m = re.match(r"^([A-Z]+)(\d{6})([CP])(\d{8})$", sym.strip())
    if not m:
        return None
    raiz, ymd, cp, strike = m.groups()
    return {
        "raiz": raiz,
        "vencimiento": f"20{ymd[0:2]}-{ymd[2:4]}-{ymd[4:6]}",
        "tipo": "call" if cp == "C" else "put",
        "strike": int(strike) / 1000.0,
    }


def _parsear(data) -> list[dict]:
    """Procesa el JSON real de MarketSnack ({"list": [...]}) a filas útiles."""
    filas: list[dict] = []
    for it in (data.get("list", []) if isinstance(data, dict) else data) or []:
        if not isinstance(it, dict):
            continue
        occ = _parse_occ(str(it.get("symbol", "")))
        if occ is None:
            continue
        filas.append({
            "strike": occ["strike"],
            "tipo": occ["tipo"],
            "vencimiento": occ["vencimiento"],
            "premium": it.get("premium"),
            "sentiment": it.get("sentiment"),
            "side": it.get("side"),
            "delta": it.get("delta"),
            "oi": it.get("open_interest"),
            "volumen": it.get("size"),
            "subyacente": it.get("asset_price"),
        })
    return filas
