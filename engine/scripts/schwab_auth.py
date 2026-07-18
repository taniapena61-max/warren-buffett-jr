"""Asistente de autorización OAuth de Schwab (paso único, lo hace el usuario).

El motor NUNCA puede hacer login por ti. Este script te da la URL para que
TÚ inicies sesión en Schwab y autorices; luego pegas aquí la URL a la que te
redirigió el navegador, y el script intercambia el código por tokens y los
guarda (en API/schwab_tokens.json, ignorado por git).

Requisitos previos (en el portal de desarrollador de Schwab):
  1. Tu app debe estar en estado "Ready for use".
  2. La Callback URL registrada debe COINCIDIR con SCHWAB_CALLBACK_URL de
     tu API/.env (por defecto https://127.0.0.1).

Uso:
    python scripts/schwab_auth.py
"""

from __future__ import annotations

import sys
from urllib.parse import parse_qs, urlparse

from wbj.config import load_settings
from wbj.providers.schwab import SchwabProvider


def main() -> int:
    s = load_settings()
    if not (s.schwab_app_key and s.schwab_app_secret):
        print("Faltan SCHWAB_APP_KEY / SCHWAB_APP_SECRET en API/.env.")
        return 1

    schwab = SchwabProvider(
        s.schwab_app_key, s.schwab_app_secret,
        s.schwab_callback_url, s.schwab_token_path,
    )

    print("\n=== Autorización de Charles Schwab (una sola vez) ===\n")
    print("1. Abre esta URL en tu navegador e inicia sesión en Schwab:\n")
    print("   " + schwab.authorize_url() + "\n")
    print("2. Autoriza el acceso. El navegador te redirigirá a una URL que")
    print(f"   empieza con {s.schwab_callback_url} y contiene ?code=...")
    print("   (puede mostrar 'no se puede acceder al sitio' — es normal;")
    print("    lo que importa es la URL de la barra de direcciones).\n")
    redirected = input("3. Pega aquí la URL COMPLETA a la que te redirigió:\n   ").strip()

    code = None
    if redirected.startswith("http"):
        qs = parse_qs(urlparse(redirected).query)
        code = (qs.get("code") or [None])[0]
    elif redirected:
        code = redirected  # por si el usuario pegó solo el code

    if not code:
        print("\nNo encontré un 'code' en lo que pegaste. Intenta de nuevo.")
        return 1

    print("\nIntercambiando el código por tokens…")
    if schwab.exchange_code(code):
        print(f"Listo. Tokens guardados en {s.schwab_token_path}.")
        print("El sistema ya puede usar precios en tiempo real de Schwab.")
        print("Nota: el refresh token dura ~7 días; después habrá que repetir esto.")
        return 0

    print("Falló el intercambio. Verifica que la Callback URL registrada en")
    print("el portal de Schwab coincida con SCHWAB_CALLBACK_URL, y que el")
    print("código no haya expirado (dura poco — repite el paso 1 si hace falta).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
