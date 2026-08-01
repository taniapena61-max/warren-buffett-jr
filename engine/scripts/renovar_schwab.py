"""Renovación de Schwab de un clic (para Tania — sin terminal, sin lag).

Qué hace, en orden:
  1. Genera la URL de autorización de Schwab.
  2. Abre tu navegador en esa URL automáticamente.
  3. Inicias sesión en Schwab y autorizas (eso lo haces TÚ, el motor nunca
     hace login por ti).
  4. Schwab te redirige a https://127.0.0.1/?code=...  (dirá "no se puede
     acceder al sitio" — es normal). Copias esa dirección de la barra.
  5. La pegas AQUÍ mismo, en esta ventana, y el canje ocurre al instante.

Por qué existe (y no lo hacemos por el chat): el 'code' de Schwab caduca en
segundos. Pegarlo directamente aquí lo intercambia en el mismo momento, sin el
ida-y-vuelta que lo dejaba expirar.

Uso normal: doble clic en "Renovar Schwab.bat".
"""

from __future__ import annotations

import sys
import webbrowser
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from wbj.config import load_settings
from wbj.providers.schwab import SchwabProvider


def _fmt(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def main() -> int:
    s = load_settings()
    if not (s.schwab_app_key and s.schwab_app_secret):
        print("Faltan SCHWAB_APP_KEY / SCHWAB_APP_SECRET en API/.env.")
        return 1

    schwab = SchwabProvider(
        s.schwab_app_key, s.schwab_app_secret,
        s.schwab_callback_url, s.schwab_token_path,
    )

    url = schwab.authorize_url()
    print("\n=== Renovar acceso a Charles Schwab ===\n")
    print("1. Te voy a abrir el navegador en la pantalla de Schwab.")
    print("   Si no se abre solo, copia y pega esta dirección en Chrome:\n")
    print("   " + url + "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("2. Inicia sesión y da 'Aceptar / Authorize'.")
    print("   (La pantalla de seguridad tarda ~30 seg — es normal, no la cierres.)\n")
    print("3. Cuando te mande a una página que dice 'no se puede acceder al")
    print("   sitio' (empieza con https://127.0.0.1/?code=...), copia esa")
    print("   dirección COMPLETA de la barra de arriba.\n")

    redirected = input("4. Pégala aquí y presiona Enter:\n   ").strip()

    code = None
    if redirected.startswith("http"):
        code = (parse_qs(urlparse(redirected).query).get("code") or [None])[0]
    elif redirected:
        code = redirected  # por si pegó solo el code

    if not code:
        print("\nNo encontré un 'code' en lo que pegaste. Vuelve a correr esto.")
        return 1

    print("\nCanjeando el código por un token nuevo…")
    if not schwab.exchange_code(code):
        print("\nFalló el canje. Casi siempre es porque el código ya expiró")
        print("(dura pocos segundos). Vuelve a correr esto y pega la URL más")
        print("rápido, o verifica que la Callback URL en el portal de Schwab")
        print("coincida con " + s.schwab_callback_url + ".")
        return 1

    tk = schwab._load_tokens() or {}
    print("\n¡Listo! Token renovado y guardado.")
    if tk.get("refresh_saved_at"):
        vence = tk["refresh_saved_at"] + 7 * 86400
        print("Vale otra semana — vence aprox: " + _fmt(vence) + ".")
    print("El sistema ya vuelve a tener precio en vivo de Schwab.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
