"""Mantiene viva la sesión de MarketSnack — renovación automática de la cookie.

MarketSnack renueva `_market_snack_session` en cada respuesta. Este script hace
UNA petición ligera; el proveedor captura la cookie nueva y la guarda. Corriéndolo
un par de veces al día, la sesión nunca caduca — sin contraseña, sin intervención.

Si la cookie ya caducó del todo (respuesta 401/403), avisa: hay que volver a
entrar a MarketSnack y pegar la cookie nueva (una vez).

Uso:  python scripts/marketsnack_keepalive.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wbj.config import load_settings  # noqa: E402
from wbj.providers.marketsnack import MarketSnackProvider  # noqa: E402


def main() -> int:
    s = load_settings()
    ms = MarketSnackProvider(s.marketsnack_cookie, cookie_path=s.marketsnack_cookie_path)
    if not ms.configured:
        print("MarketSnack: sin cookie configurada (nada que mantener)")
        return 0
    r = ms.fetch_flow("SPX")  # petición ligera; refresca la cookie
    if r.get("error"):
        print(f"MarketSnack keepalive FALLÓ: {r['error']}")
        # 'caducada' => Tania debe re-loguear; lo señalamos con exit 2
        return 2 if "caduc" in r["error"] else 1
    n = len(r.get("data", {}).get("list", []) if isinstance(r.get("data"), dict) else [])
    print(f"MarketSnack keepalive OK — sesión renovada ({n} filas SPX)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
