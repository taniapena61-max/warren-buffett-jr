"""Charles Schwab market-data provider (read-only, OAuth 2.0).

Real-time quotes from the Schwab Market Data API, used to sharpen the live
price the rest of the engine reads. READ-ONLY by design: this module talks
only to the quotes endpoint. It never touches trading, orders, positions,
or funds — the project analyzes and informs, it does not execute (CLAUDE.md
scope), and there is deliberately no method here that could place a trade.

Schwab uses 3-legged OAuth. The account holder authorizes once in a browser
(only the user can log in — never the engine); the returned code is
exchanged for an access token (~30-min TTL) and a refresh token (~7-day
TTL). `scripts/schwab_auth.py` walks the user through that one-time step.
This provider then refreshes the access token automatically until the
refresh token expires, after which the user must re-authorize.

Tokens live in a gitignored JSON file under API/ (never printed, never
committed). No secret is ever logged.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

_BASE = "https://api.schwabapi.com"
_AUTHORIZE = f"{_BASE}/v1/oauth/authorize"
_TOKEN = f"{_BASE}/v1/oauth/token"
_QUOTES = f"{_BASE}/marketdata/v1/quotes"

_ACCESS_TTL_GUARD = 60  # refresh this many seconds before nominal expiry.
_REFRESH_TTL_DAYS = 7   # Schwab refresh tokens expire after ~7 days.


class SchwabProvider:
    """Read-only Schwab market-data provider (real-time quotes)."""

    def __init__(
        self,
        app_key: str | None,
        app_secret: str | None,
        callback_url: str,
        token_path: Path,
        client: httpx.Client | None = None,
        history_dir: Path | None = None,
    ) -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.callback_url = callback_url
        self.token_path = token_path
        self.client = client if client is not None else httpx.Client(timeout=10.0)
        # Si se da, cada cotizacion exitosa se archiva (una fila por dia).
        # Schwab no guarda historial; asi lo vamos construyendo nosotros.
        self.history_dir = history_dir

    # --- configuration state -------------------------------------------------

    @property
    def configured(self) -> bool:
        """True iff the app key/secret are present (OAuth can be started)."""
        return bool(self.app_key and self.app_secret)

    @property
    def available(self) -> bool:
        """True iff configured AND an authorized token file exists.

        Does not guarantee the refresh token is still valid — `last_price`
        returns None (and logs a re-auth hint) if refreshing fails.
        """
        return self.configured and self.token_path.exists()

    def _basic_auth(self) -> str:
        raw = f"{self.app_key}:{self.app_secret}".encode()
        return base64.b64encode(raw).decode()

    # --- OAuth ---------------------------------------------------------------

    def authorize_url(self) -> str:
        """The URL the user opens to log in and authorize (one-time).

        `redirect_uri` is URL-encoded — Schwab rejects the request otherwise.
        """
        redirect = quote(self.callback_url, safe="")
        return (
            f"{_AUTHORIZE}?client_id={self.app_key}"
            f"&redirect_uri={redirect}&response_type=code"
        )

    def exchange_code(self, code: str) -> bool:
        """Exchange an authorization code for tokens and persist them."""
        return self._token_request({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.callback_url,
        })

    def _refresh(self, refresh_token: str) -> bool:
        return self._token_request({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        })

    def _token_request(self, form: dict[str, str]) -> bool:
        headers = {
            "Authorization": f"Basic {self._basic_auth()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            r = self.client.post(_TOKEN, data=form, headers=headers)
        except httpx.HTTPError:
            return False
        if r.status_code != 200:
            return False
        try:
            payload = r.json()
        except ValueError:
            return False
        self._save_tokens(payload)
        return True

    def _save_tokens(self, payload: dict[str, Any]) -> None:
        now = time.time()
        prev = self._load_tokens() or {}
        new_rt = payload.get("refresh_token")
        # Preserve the existing refresh token when a plain access-token
        # refresh doesn't return one. Only reset the 7-day refresh clock when
        # a genuinely NEW refresh token is issued: if Schwab ever rotates it
        # on refresh, we stay authorized indefinitely; if it doesn't (its
        # current behavior), the 7-day wall stays measured from the original
        # authorization, so we prompt re-auth at the right time instead of
        # trusting a token that's really already dead.
        rotated = bool(new_rt) and new_rt != prev.get("refresh_token")
        tokens = {
            "access_token": payload.get("access_token"),
            "refresh_token": new_rt or prev.get("refresh_token"),
            "access_expires_at": now + float(payload.get("expires_in", 1800)),
            "refresh_saved_at": now if rotated else prev.get("refresh_saved_at", now),
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
        """Return a fresh access token, refreshing if needed. None if re-auth
        is required (missing tokens, or the refresh token itself expired)."""
        tokens = self._load_tokens()
        if not tokens:
            return None
        now = time.time()
        # Refresh token past its ~7-day life -> the user must re-authorize.
        saved = tokens.get("refresh_saved_at", 0)
        if now - saved > _REFRESH_TTL_DAYS * 86400:
            return None
        if now < tokens.get("access_expires_at", 0) - _ACCESS_TTL_GUARD:
            return tokens.get("access_token")
        # Access token stale: refresh it.
        rt = tokens.get("refresh_token")
        if not rt or not self._refresh(rt):
            return None
        refreshed = self._load_tokens() or {}
        return refreshed.get("access_token")

    # --- market data (read-only) --------------------------------------------

    def quote(self, symbol: str) -> dict | None:
        """Real-time quote fields for `symbol`, or None if unavailable."""
        token = self._valid_access_token()
        if not token:
            return None
        try:
            r = self.client.get(
                _QUOTES,
                params={"symbols": symbol.upper()},
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.HTTPError:
            return None
        if r.status_code != 200:
            return None
        try:
            data = r.json()
        except ValueError:
            return None
        entry = data.get(symbol.upper())
        if not isinstance(entry, dict):
            return None
        q = entry.get("quote") or entry
        if self.history_dir is not None and isinstance(q, dict):
            try:  # archivar nunca debe romper una cotizacion
                from wbj.history import registrar_quote
                registrar_quote(symbol.upper(), q, self.history_dir)
            except Exception:  # noqa: BLE001
                pass
        return q

    def last_price(self, symbol: str) -> float | None:
        """Latest real-time price for `symbol`, or None."""
        q = self.quote(symbol)
        if not isinstance(q, dict):
            return None
        for key in ("lastPrice", "mark", "closePrice"):
            v = q.get(key)
            if isinstance(v, (int, float)) and v > 0:
                return float(v)
        return None
