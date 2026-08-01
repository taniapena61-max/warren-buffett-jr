"""Conexión de TradeStation SIN copiar nada (para Tania — de un clic).

El problema con OAuth en localhost: el navegador te redirige a
http://localhost:3000/?code=...  pero ahí no hay nada escuchando, así que la
página falla y batallas para copiar la URL antes de que el código expire.

La solución: este script levanta un mini-servidor local en ese puerto, ATRAPA
el código automáticamente en el instante que el navegador te redirige, y hace
el canje al momento (sin copiar, sin que expire).

Flujo:
  1. Si no hay API Key guardada, la pegas una vez (se guarda en API/.env).
  2. Se abre el navegador en TradeStation → inicias sesión → Allow.
  3. Al redirigir, el servidor atrapa el code y canjea los tokens solo.
  4. Listo. (Si algo falla, cae a pegar la URL a mano.)

Uso normal: doble clic en "Renovar TradeStation.bat".
"""

from __future__ import annotations

import http.server
import sys
from urllib.parse import parse_qs, urlparse

from wbj.config import load_settings
from wbj.providers.tradestation import TradeStationProvider

_captured: dict[str, str | None] = {}


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        params = parse_qs(urlparse(self.path).query)
        code = (params.get("code") or [None])[0]
        if code:
            _captured["code"] = code
        ok = code is not None
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = ("¡Listo! Ya puedes cerrar esta pestaña y volver a la ventana."
               if ok else "No llegó el código — vuelve a correr la conexión.")
        self.wfile.write(
            f"<html><body style='font-family:sans-serif;text-align:center;"
            f"margin-top:60px'><h2>{msg}</h2></body></html>".encode("utf-8"))

    def log_message(self, *args) -> None:  # silencio en consola
        pass


def _guardar_en_env(repo_root, updates: dict[str, str]) -> None:
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
    if not s.tradestation_client_id:
        print("Primera conexión con TradeStation.\n")
        key = input("Pega aquí tu API Key (client_id) y presiona Enter:\n   ").strip()
        if not key:
            print("\nNo pegaste nada. Vuelve a correr esto.")
            return 1
        _guardar_en_env(s.repo_root, {"TRADESTATION_CLIENT_ID": key})
        s = load_settings()
        print("\nAPI Key guardada de forma segura en API/.env.\n")

    if not s.tradestation_client_secret:
        print("Tu app de TradeStation es tipo 'Regular Web App' y necesita un")
        print("'Client Secret' además del API Key. Está junto a tu API Key (en el")
        print("portal o en el correo; a veces hay que dar clic en 'reveal/mostrar').")
        sec = input("Pega tu Client Secret (o Enter si de plano no tiene):\n   ").strip()
        if sec:
            _guardar_en_env(s.repo_root, {"TRADESTATION_CLIENT_SECRET": sec})
            s = load_settings()
            print("\nSecret guardado de forma segura en API/.env.\n")

    ts = TradeStationProvider(
        s.tradestation_client_id, s.tradestation_client_secret,
        s.tradestation_callback_url, s.tradestation_token_path,
    )

    parsed = urlparse(s.tradestation_callback_url)
    port = parsed.port or 80

    # Servidor PRIMERO, antes de abrir el navegador: si TradeStation redirige de
    # inmediato (ya con sesión iniciada), el servidor ya está escuchando y no se
    # pierde el código por una carrera. Bind a 127.0.0.1 (no "localhost") para
    # evitar que Python escuche solo en IPv6 ::1 mientras el navegador llega por
    # IPv4 — esa desconexión era justo lo que fallaba.
    try:
        server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    except OSError as e:
        print(f"No pude abrir el puerto {port} ({e}). Cierra otros programas que")
        print("lo usen, o dime y cambiamos el puerto.")
        return 1
    server.timeout = 300  # espera hasta 5 min a que autorices, sin prisa

    import webbrowser
    url = ts.authorize_url()
    print("=== Conectar TradeStation (sin copiar nada) ===\n")
    print("1. Te abro el navegador en TradeStation. Si no abre solo, pega esto:\n")
    print("   " + url + "\n")
    print("2. Inicia sesión y da 'Allow'. Yo atrapo el código automáticamente —")
    print("   NO tienes que copiar nada. Tómate tu tiempo.\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    intentos = 0
    while "code" not in _captured and intentos < 40:
        server.handle_request()  # atiende una petición (redirect o favicon)
        intentos += 1
    server.server_close()

    code = _captured.get("code")
    if not code:
        # Respaldo manual por si el navegador no llegó al servidor.
        print("No atrapé el código automáticamente.")
        pegado = input("Pega aquí la URL http://localhost... a la que te "
                       "redirigió (si la tienes):\n   ").strip()
        if pegado.startswith("http"):
            code = (parse_qs(urlparse(pegado).query).get("code") or [None])[0]
        elif pegado:
            code = pegado
    if not code:
        print("\nSin código. Vuelve a correr esto.")
        return 1

    print("\nCanjeando el código por tokens…")
    if not ts.exchange_code(code):
        err = ts._last_token_error or "desconocido"
        try:
            (s.repo_root / "ts_auth_error.log").write_text(err, encoding="utf-8")
        except OSError:
            pass
        print("\nFalló el canje. Error de TradeStation:")
        print("   " + err)
        if "access_denied" in err or "401" in err:
            print("\n-> Falta el Client Secret (o es incorrecto). Consíguelo y")
            print("   vuelve a correr esto: te lo pedirá al inicio.")
        elif "invalid_grant" in err:
            print("\n-> El código expiró o ya se usó. Solo vuelve a correr esto.")
        else:
            print("\n-> Cópiame este error y lo resolvemos.")
        return 1

    print("\n¡Listo! TradeStation conectado y tokens guardados.")
    print("Su refresh token es de larga vida: no renuevas cada semana.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
