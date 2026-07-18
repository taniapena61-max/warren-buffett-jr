"""Tests for the EMA-200 discount add-on (Tania's entry strategy)."""

import httpx

from wbj.ema_discount import TAKE_PROFIT, ema200_status


def _yahoo_response(closes):
    return httpx.Response(
        200,
        json={"chart": {"result": [{"indicators": {"adjclose": [{"adjclose": closes}]}}]}},
    )


def test_below_ema200_is_a_discount():
    # 260 flat closes at 100 -> EMA200 == 100; price 80 is a 20% discount.
    c = httpx.Client(transport=httpx.MockTransport(lambda r: _yahoo_response([100.0] * 260)))
    st = ema200_status("TEST", 80.0, client=c)
    assert st["ema200"] == 100.0
    assert st["below_ema200"] is True
    assert st["discount"] == -0.20
    assert st["take_profit_25"] == round(80.0 * (1 + TAKE_PROFIT), 2) == 100.0


def test_above_ema200_is_not_a_discount():
    c = httpx.Client(transport=httpx.MockTransport(lambda r: _yahoo_response([100.0] * 260)))
    st = ema200_status("TEST", 120.0, client=c)
    assert st["below_ema200"] is False
    assert st["discount"] == 0.20


def test_short_history_is_not_scorable():
    c = httpx.Client(transport=httpx.MockTransport(lambda r: _yahoo_response([100.0] * 50)))
    assert ema200_status("TEST", 100.0, client=c)["ema200"] is None


def test_no_price_is_not_scorable():
    # Must not even hit the network without a price.
    dead = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    assert ema200_status("TEST", None, client=dead)["below_ema200"] is None
