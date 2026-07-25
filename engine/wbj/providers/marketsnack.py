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

# Placeholder: la URL real de la petición de datos (NO la de la página).
# Tania la copia de DevTools → Network → flow_feed → Request URL.
_FLOW_URL = "https://app.marketsnack.com/api/flow_feed"  # <-- confirmar


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
            "User-Agent": "Mozilla/5.0 warren-buffett-jr",
            "Accept": "application/json",
        }

    def fetch_flow(self, symbol: str = "IREN", params: dict | None = None) -> dict:
        """Baja el feed crudo. {"error": ...} si falla o la cookie caducó."""
        if not self._cookie:
            return {"error": "falta MARKETSNACK_COOKIE en API/.env"}
        q = {"symbol": symbol, "sort": "-premium"}
        if params:
            q.update(params)
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

    def strikes_para_confluencia(self, symbol: str = "SPX") -> list[float]:
        """Extrae los strikes de mayor premium para el mapa de confluencia.

        PENDIENTE: adaptar `_parsear` al formato real de la respuesta.
        """
        r = self.fetch_flow(symbol)
        if r.get("error"):
            return []
        return _parsear(r["data"])


def _parsear(data) -> list[float]:
    """Extrae strikes del JSON de MarketSnack. Se completa con la respuesta real.

    De las capturas, cada fila tiene contrato tipo 'IREN Aug 21 32P' con premium,
    delta, IV, OI. Aquí se sacarían los strikes de las filas de mayor premium.
    """
    strikes: list[float] = []
    filas = data if isinstance(data, list) else data.get("rows", data.get("data", []))
    for f in filas or []:
        if isinstance(f, dict):
            k = f.get("strike") or f.get("strikePrice")
            if isinstance(k, (int, float)):
                strikes.append(float(k))
    return strikes
