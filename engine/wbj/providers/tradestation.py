"""TradeStation market-data provider (read-only, OAuth 2.0).

Espejo del provider de Schwab, pero para TradeStation. READ-ONLY por diseño:
habla solo con market data (quotes, cadenas de opciones) y con la lectura de
cuentas/posiciones. NUNCA toca órdenes ni fondos — el proyecto analiza e
informa, no ejecuta (alcance de CLAUDE.md), y deliberadamente aquí no existe
ningún método que pueda mandar una orden.

TradeStation usa OAuth 2.0 (Auth Code, vía Auth0 en signin.tradestation.com).
El dueño de la cuenta autoriza una sola vez en el navegador (solo el usuario
puede iniciar sesión — nunca el motor); el código se cambia por un access token
(~20 min de vida) y un refresh token de **larga vida** (no caduca a los 7 días
como Schwab). `scripts/tradestation_auth.py` guía ese paso único. Después este
provider refresca el access token solo.

Los tokens viven en un JSON gitignored bajo API/ (nunca se imprime ni commitea).
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

_SIGNIN = "https://signin.tradestation.com"
_AUTHORIZE = f"{_SIGNIN}/authorize"
_TOKEN = f"{_SIGNIN}/oauth/token"
_AUDIENCE = "https://api.tradestation.com"

_API = "https://api.tradestation.com/v3"
_QUOTES = f"{_API}/marketdata/quotes"
_EXPIRATIONS = f"{_API}/marketdata/options/expirations"
_ACCOUNTS = f"{_API}/brokerage/accounts"

# Scopes read-only + refresh. Trade NO se pide: este provider no ejecuta.
_SCOPES = "openid profile offline_access MarketData ReadAccount"
_ACCESS_TTL_GUARD = 60   # refresca este número de segundos antes del vencimiento
_ACCESS_TTL_DEFAULT = 1200  # los access tokens de TradeStation duran ~20 min


class TradeStationProvider:
    """Read-only TradeStation market-data provider (quotes/cadenas/posiciones)."""

    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        callback_url: str,
        token_path: Path,
        client: httpx.Client | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret  # opcional: apps públicas usan PKCE
        self.callback_url = callback_url
        self.token_path = token_path
        self.client = client if client is not None else httpx.Client(timeout=15.0)
        # PKCE: para apps públicas (sin secret). El verifier se genera una vez por
        # instancia; authorize_url() manda su challenge y exchange_code() manda el
        # verifier. renovar_tradestation.py usa la MISMA instancia, así que cuadran.
        self._code_verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(self._code_verifier.encode()).digest()
        self._code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
        self._last_token_error: str | None = None  # dx del último canje fallido

    # --- estado de configuración --------------------------------------------

    @property
    def configured(self) -> bool:
        """True si hay client_id (con o sin secret: las apps públicas usan PKCE)."""
        return bool(self.client_id)

    @property
    def available(self) -> bool:
        """True si está configurado Y existe un archivo de token autorizado."""
        return self.configured and self.token_path.exists()

    # --- OAuth ---------------------------------------------------------------

    def authorize_url(self) -> str:
        """URL que el usuario abre para iniciar sesión y autorizar (una vez)."""
        redirect = quote(self.callback_url, safe="")
        scope = quote(_SCOPES, safe="")
        audience = quote(_AUDIENCE, safe="")
        return (
            f"{_AUTHORIZE}?response_type=code&client_id={self.client_id}"
            f"&audience={audience}&redirect_uri={redirect}"
            f"&scope={scope}&state=wbj"
            f"&code_challenge={self._code_challenge}&code_challenge_method=S256"
        )

    def exchange_code(self, code: str) -> bool:
        """Cambia un código de autorización por tokens y los persiste."""
        form = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": self.callback_url,
            "code_verifier": self._code_verifier,  # PKCE (apps públicas)
        }
        if self.client_secret:  # apps confidenciales también mandan el secret
            form["client_secret"] = self.client_secret
        return self._token_request(form)

    def _refresh(self, refresh_token: str) -> bool:
        form = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
        }
        if self.client_secret:
            form["client_secret"] = self.client_secret
        return self._token_request(form)

    def _token_request(self, form: dict[str, str | None]) -> bool:
        # TradeStation manda client_id/secret en el cuerpo (no Basic auth).
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            r = self.client.post(_TOKEN, data=form, headers=headers)
        except httpx.HTTPError as e:
            self._last_token_error = f"red: {type(e).__name__}"
            return False
        if r.status_code != 200:
            # El cuerpo de error de OAuth no trae secretos (solo error/desc).
            self._last_token_error = f"{r.status_code}: {r.text[:300]}"
            return False
        try:
            payload = r.json()
        except ValueError:
            self._last_token_error = "respuesta no-JSON del endpoint de token"
            return False
        self._last_token_error = None
        self._save_tokens(payload)
        return True

    def _save_tokens(self, payload: dict[str, Any]) -> None:
        now = time.time()
        prev = self._load_tokens() or {}
        # TradeStation no siempre devuelve refresh_token al refrescar: se conserva
        # el anterior. Su refresh token es de larga vida (no hay muro de 7 días).
        new_rt = payload.get("refresh_token") or prev.get("refresh_token")
        tokens = {
            "access_token": payload.get("access_token"),
            "refresh_token": new_rt,
            "access_expires_at": now + float(payload.get("expires_in", _ACCESS_TTL_DEFAULT)),
            "refresh_saved_at": prev.get("refresh_saved_at", now)
            if prev.get("refresh_token") == new_rt else now,
        }
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(json.dumps(tokens), encoding="utf-8")

    def _load_tokens(self) -> dict | None:
        if not self.token_path.exists():
            return None
        try:
            return json.loads(self.token_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _valid_access_token(self) -> str | None:
        """Devuelve un access token fresco, refrescando si hace falta. None si
        se requiere re-autorizar (faltan tokens o el refresh falló)."""
        tokens = self._load_tokens()
        if not tokens:
            return None
        now = time.time()
        if now < tokens.get("access_expires_at", 0) - _ACCESS_TTL_GUARD:
            return tokens.get("access_token")
        rt = tokens.get("refresh_token")
        if not rt or not self._refresh(rt):
            return None
        return (self._load_tokens() or {}).get("access_token")

    # --- market data (read-only) --------------------------------------------

    def _get(self, url: str) -> dict | None:
        token = self._valid_access_token()
        if not token:
            return None
        try:
            r = self.client.get(url, headers={"Authorization": f"Bearer {token}"})
        except httpx.HTTPError:
            return None
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except ValueError:
            return None

    def quote(self, symbol: str) -> dict | None:
        """Cotización en tiempo real de `symbol` (formato de símbolo de TS)."""
        data = self._get(f"{_QUOTES}/{quote(symbol, safe='')}")
        if not data:
            return None
        quotes = data.get("Quotes") or []
        return quotes[0] if quotes else None

    def option_expirations(self, underlying: str) -> dict | None:
        """Vencimientos de opciones disponibles para `underlying`."""
        return self._get(f"{_EXPIRATIONS}/{quote(underlying, safe='')}")

    def accounts(self) -> dict | None:
        """Cuentas de brokerage (solo lectura)."""
        return self._get(_ACCOUNTS)

    def positions(self, account_ids: str) -> dict | None:
        """Posiciones de una o varias cuentas (coma-separadas, solo lectura)."""
        return self._get(f"{_ACCOUNTS}/{quote(account_ids, safe='')}/positions")
