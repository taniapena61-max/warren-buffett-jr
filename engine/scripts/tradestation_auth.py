"""Asistente de autorización OAuth de TradeStation (paso único, lo hace el usuario).

El motor NUNCA puede hacer login por ti. Este script te da la URL para que TÚ
inicies sesión en TradeStation y autorices; luego pegas la URL a la que te
redirigió el navegador, y el script cambia el código por tokens y los guarda
(en API/tradestation_tokens.json, ignorado por git).

Requisitos previos (en developer.tradestation.com):
  1. Tu API key (client_id) y secret en API/.env como TRADESTATION_CLIENT_ID /
     TRADESTATION_CLIENT_SECRET.
  2. La Redirect URI registrada en TradeStation debe COINCIDIR con
     TRADESTATION_CALLBACK_URL de tu API/.env (por defecto http://localhost:3000).

Uso:
    python scripts/tradestation_auth.py
"""

from __future__ import annotations

import sys
from urllib.parse import parse_qs, urlparse

from wbj.config import load_settings
from wbj.providers.tradestation import TradeStationProvider


def main() -> int:
    s = load_settings()
    if not s.tradestation_client_id:
        print("Falta TRADESTATION_CLIENT_ID en API/.env. (El Secret no hace falta:")
        print("app pública / PKCE.)")
        return 1

    ts = TradeStationProvider(
        s.tradestation_client_id, s.tradestation_client_secret,
        s.tradestation_callback_url, s.tradestation_token_path,
    )

    print("\n=== Autorización de TradeStation (una sola vez) ===\n")
    print("1. Abre esta URL en tu navegador e inicia sesión en TradeStation:\n")
    print("   " + ts.authorize_url() + "\n")
    print("2. Autoriza el acceso. El navegador te redirigirá a una URL que")
    print(f"   empieza con {s.tradestation_callback_url} y contiene ?code=...")
    print("   (puede mostrar 'no se puede acceder al sitio' — es normal;")
    print("    lo que importa es la URL de la barra de direcciones).\n")
    redirected = input("3. Pega aquí la URL COMPLETA a la que te redirigió:\n   ").strip()

    code = None
    if redirected.startswith("http"):
        qs = parse_qs(urlparse(redirected).query)
        code = (qs.get("code") or [None])[0]
    elif redirected:
        code = redirected  # por si pegaste solo el code

    if not code:
        print("\nNo encontré un 'code' en lo que pegaste. Intenta de nuevo.")
        return 1

    print("\nIntercambiando el código por tokens…")
    if ts.exchange_code(code):
        print(f"Listo. Tokens guardados en {s.tradestation_token_path}.")
        print("El sistema ya puede usar datos de TradeStation.")
        print("Nota: el refresh token de TradeStation es de larga vida — renovarás")
        print("mucho menos seguido que Schwab.")
        return 0

    print("Falló el intercambio. Verifica que la Redirect URI registrada en")
    print("TradeStation coincida con TRADESTATION_CALLBACK_URL, y que el código")
    print("no haya expirado (dura poco — repite el paso 1 si hace falta).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
