"""Tests for wbj.providers.schwab.SchwabProvider (read-only, mocked OAuth)."""

import json
import time

import httpx
import pytest

from wbj.providers.schwab import SchwabProvider


def _provider(tmp_path, handler, key="appkey", secret="secret"):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return SchwabProvider(key, secret, "https://127.0.0.1",
                          tmp_path / "schwab_tokens.json", client=client)


def _write_tokens(p, access="AT", refresh="RT", access_age=0, refresh_age=0):
    now = time.time()
    p.write_text(json.dumps({
        "access_token": access,
        "refresh_token": refresh,
        "access_expires_at": now - access_age + 1800,
        "refresh_saved_at": now - refresh_age,
    }), encoding="utf-8")


# --- configuration state ----------------------------------------------------


def test_configured_needs_key_and_secret(tmp_path):
    assert _provider(tmp_path, lambda r: httpx.Response(200)).configured is True
    assert _provider(tmp_path, lambda r: httpx.Response(200), key=None).configured is False


def test_available_needs_token_file(tmp_path):
    p = _provider(tmp_path, lambda r: httpx.Response(200))
    assert p.available is False
    _write_tokens(p.token_path)
    assert p.available is True


def test_authorize_url_contains_client_and_encoded_callback(tmp_path):
    p = _provider(tmp_path, lambda r: httpx.Response(200))
    url = p.authorize_url()
    assert "client_id=appkey" in url
    # redirect_uri must be URL-encoded or Schwab rejects the request.
    assert "redirect_uri=https%3A%2F%2F127.0.0.1" in url
    assert "response_type=code" in url


# --- token exchange / refresh -----------------------------------------------


def test_exchange_code_persists_tokens(tmp_path):
    captured = {}

    def handler(request):
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = request.content.decode()
        return httpx.Response(200, json={
            "access_token": "new-at", "refresh_token": "new-rt", "expires_in": 1800,
        })

    p = _provider(tmp_path, handler)
    assert p.exchange_code("THECODE") is True
    # Basic auth header, not the raw secret in the body.
    assert captured["auth"].startswith("Basic ")
    assert "grant_type=authorization_code" in captured["body"]
    tokens = json.loads(p.token_path.read_text())
    assert tokens["access_token"] == "new-at"
    assert tokens["refresh_token"] == "new-rt"


def test_exchange_code_returns_false_on_error(tmp_path):
    p = _provider(tmp_path, lambda r: httpx.Response(400, json={"error": "bad"}))
    assert p.exchange_code("x") is False
    assert not p.token_path.exists()


def test_valid_access_token_refreshes_when_stale(tmp_path):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(200, json={
            "access_token": "refreshed", "refresh_token": "RT2", "expires_in": 1800,
        })

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, access="old", access_age=1800)  # already expired
    token = p._valid_access_token()
    assert token == "refreshed"
    assert calls["n"] == 1  # a refresh happened


def test_valid_access_token_uses_cached_when_fresh(tmp_path):
    def handler(request):
        raise AssertionError("must not hit network when access token is fresh")

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, access="fresh")
    assert p._valid_access_token() == "fresh"


def test_refresh_preserves_token_when_none_returned(tmp_path):
    """A plain access-token refresh may omit the refresh token; keep the old."""
    def handler(request):
        return httpx.Response(200, json={"access_token": "new", "expires_in": 1800})

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, refresh="KEEPME", access_age=1800)
    p._valid_access_token()
    tokens = json.loads(p.token_path.read_text())
    assert tokens["refresh_token"] == "KEEPME"


def test_same_refresh_token_does_not_extend_7day_wall(tmp_path):
    """If Schwab returns the SAME refresh token, the 7-day clock must not
    reset — otherwise we'd trust a token that's really already expiring."""
    def handler(request):
        return httpx.Response(200, json={
            "access_token": "new", "refresh_token": "SAME", "expires_in": 1800,
        })

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, refresh="SAME", access_age=1800, refresh_age=5 * 86400)
    before = json.loads(p.token_path.read_text())["refresh_saved_at"]
    p._valid_access_token()
    after = json.loads(p.token_path.read_text())["refresh_saved_at"]
    assert abs(after - before) < 2  # unchanged (still ~5 days old)


def test_new_refresh_token_resets_7day_wall(tmp_path):
    """A genuinely rotated refresh token DOES reset the clock (stay alive)."""
    def handler(request):
        return httpx.Response(200, json={
            "access_token": "new", "refresh_token": "ROTATED", "expires_in": 1800,
        })

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, refresh="OLD", access_age=1800, refresh_age=5 * 86400)
    p._valid_access_token()
    tokens = json.loads(p.token_path.read_text())
    assert tokens["refresh_token"] == "ROTATED"
    assert time.time() - tokens["refresh_saved_at"] < 2  # clock reset to now


def test_expired_refresh_token_forces_reauth(tmp_path):
    def handler(request):
        raise AssertionError("must not attempt refresh past the 7-day window")

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, access_age=1800, refresh_age=8 * 86400)
    assert p._valid_access_token() is None


# --- quotes (read-only) -----------------------------------------------------


def test_last_price_parses_quote(tmp_path):
    def handler(request):
        assert request.url.path.endswith("/marketdata/v1/quotes")
        assert request.headers.get("Authorization") == "Bearer fresh"
        return httpx.Response(200, json={
            "AAPL": {"quote": {"lastPrice": 333.26, "bidPrice": 333.2}},
        })

    p = _provider(tmp_path, handler)
    _write_tokens(p.token_path, access="fresh")
    assert p.last_price("AAPL") == pytest.approx(333.26)


def test_last_price_none_without_tokens(tmp_path):
    def handler(request):
        raise AssertionError("no network without tokens")

    p = _provider(tmp_path, handler)
    assert p.last_price("AAPL") is None


def test_quote_none_on_http_error(tmp_path):
    p = _provider(tmp_path, lambda r: httpx.Response(401, json={"error": "unauthorized"}))
    _write_tokens(p.token_path, access="fresh")
    assert p.last_price("AAPL") is None
