"""Conexión/renovación de TradeStation de un clic (para Tania — sin terminal).

Qué hace, en orden:
  1. Genera la URL de autorización de TradeStation.
  2. Abre tu navegador en esa URL automáticamente.
  3. Inicias sesión en TradeStation y autorizas (eso lo haces TÚ; el motor
     nunca hace login por ti).
  4. TradeStation te redirige a tu Redirect URI con ?code=... (puede decir "no
     se puede acceder al sitio" — es normal). Copias esa dirección de la barra.
  5. La pegas AQUÍ mismo y el canje ocurre al instante.

El 'code' caduca en segundos; pegarlo aquí lo intercambia en el momento.

A diferencia de Schwab, el refresh token de TradeStation es de LARGA VIDA:
esto se hace una vez y no hay que repetirlo cada semana.

Uso normal: doble clic en "Renovar TradeStation.bat".
"""

from __future__ import annotations

import sys
import webbrowser
from urllib.parse import parse_qs, urlparse

from wbj.config import load_settings
from wbj.providers.tradestation import TradeStationProvider


def _guardar_en_env(repo_root, updates: dict[str, str]) -> None:
    """Actualiza o agrega KEY=valor en API/.env sin tocar el resto del archivo."""
    env = repo_root / "API" / ".env"
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    out, vistas = [], set()
    for line in lines:
        clave = line.split("=", 1)[0].strip() if "=" in line else None
        if clave in updates:
            out.append(f"{clave}={updates[clave]}")
            vistas.add(clave)
        else:
            out.append(line)
    for clave, valor in updates.items():
        if clave not in vistas:
            out.append(f"{clave}={valor}")
    env.parent.mkdir(parents=True, exist_ok=True)
    env.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    s = load_settings()
    # Primera vez: si no hay API Key guardada, la pedimos aquí mismo y la
    # guardamos en API/.env (gitignored). Así todo es un solo doble clic, sin
    # que Tania edite archivos. La app es pública (PKCE): NO se pide Secret.
    if not s.tradestation_client_id:
        print("Primera conexión con TradeStation.\n")
        key = input("Pega aquí tu API Key (client_id) y presiona Enter:\n   ").strip()
        if not key:
            print("\nNo pegaste nada. Vuelve a correr esto.")
            return 1
        _guardar_en_env(s.repo_root, {"TRADESTATION_CLIENT_ID": key})
        s = load_settings()  # recargar con la key ya guardada
        print("\nAPI Key guardada de forma segura en API/.env.\n")

    ts = TradeStationProvider(
        s.tradestation_client_id, s.tradestation_client_secret,
        s.tradestation_callback_url, s.tradestation_token_path,
    )

    url = ts.authorize_url()
    print("\n=== Conectar / renovar TradeStation ===\n")
    print("1. Te voy a abrir el navegador en la pantalla de TradeStation.")
    print("   Si no se abre solo, copia y pega esta dirección en Chrome:\n")
    print("   " + url + "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("2. Inicia sesión y da 'Allow / Authorize'.")
    print("3. Cuando te mande a una página que empieza con")
    print(f"   {s.tradestation_callback_url} y contiene ?code=..., copia esa")
    print("   dirección COMPLETA de la barra de arriba.")
    print("   (Si dice 'no se puede acceder al sitio', es normal.)\n")

    redirected = input("4. Pégala aquí y presiona Enter:\n   ").strip()

    code = None
    if redirected.startswith("http"):
        code = (parse_qs(urlparse(redirected).query).get("code") or [None])[0]
    elif redirected:
        code = redirected

    if not code:
        print("\nNo encontré un 'code' en lo que pegaste. Vuelve a correr esto.")
        return 1

    print("\nCanjeando el código por tokens…")
    if not ts.exchange_code(code):
        print("\nFalló el canje. Casi siempre es porque el código ya expiró")
        print("(dura pocos segundos). Vuelve a correr esto y pega la URL más")
        print("rápido, o verifica que la Redirect URI registrada en TradeStation")
        print("coincida EXACTO con " + s.tradestation_callback_url + ".")
        return 1

    print("\n¡Listo! TradeStation conectado y tokens guardados.")
    print("Su refresh token es de larga vida: no tienes que repetir esto cada")
    print("semana como Schwab.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
