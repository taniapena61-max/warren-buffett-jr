"""Captura automática del código OAuth de Schwab (sin copiar/pegar).

Levanta un servidor HTTPS local en la Callback URL (https://127.0.0.1),
abre el navegador en la página de login de Schwab, y cuando Schwab redirige
de vuelta con el código, lo atrapa y lo intercambia por tokens al instante —
sin que el usuario copie nada, y sin la carrera contra el reloj del método
manual.

El certificado es auto-firmado (solo para 127.0.0.1), así que el navegador
mostrará un aviso de seguridad: el usuario hace clic en "Avanzado" ->
"Continuar a 127.0.0.1 (no seguro)" una vez, y el servidor recibe el código.

Uso:
    python scripts/schwab_catch.py
"""

from __future__ import annotations

import datetime
import html
import re
import ssl
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from wbj.config import load_settings
from wbj.providers.schwab import SchwabProvider

_RESULT: dict[str, str] = {}


def _self_signed_cert() -> tuple[Path, Path]:
    """Generate a throwaway self-signed cert/key for 127.0.0.1."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1"))]), critical=False)
        .sign(key, hashes.SHA256())
    )
    d = Path(tempfile.mkdtemp())
    cert_path, key_path = d / "cert.pem", d / "key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    return cert_path, key_path


def _make_handler(schwab: SchwabProvider):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence server logs
            pass

        def do_GET(self):  # noqa: N802
            # Schwab sometimes drops the '?'; grab code= wherever it is.
            m = re.search(r"code=([^&]+)", self.path)
            if not m:
                # Codeless request (favicon, bare /, etc.): ignore and KEEP
                # serving — do not shut down waiting for the real redirect.
                self.send_response(204)
                self.end_headers()
                return
            code = unquote(m.group(1))
            ok = schwab.exchange_code(code)
            _RESULT["status"] = "ok" if ok else "fail"
            err = getattr(schwab, "last_error", "") or ""
            if not ok:
                print(f"[!] Schwab rechazo el canje: {err}", flush=True)
                try:
                    log = Path(__file__).resolve().parents[2] / "logs" / "schwab_catch_error.log"
                    with open(log, "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {err}\n")
                except OSError:
                    pass
            page = (
                "<h2>Listo. Ya puedes cerrar esta pestana.</h2>"
                if ok else
                f"<h2>El intercambio fallo. Vuelve al asistente.</h2><pre>{html.escape(err)}</pre>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<html><body style='font-family:sans-serif'>{page}</body></html>".encode())
            # Only stop once we actually handled the code.
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    return Handler


def main() -> int:
    # --escuchar: modo pasivo — NO abre el navegador y espera a que el usuario
    # haga clic en el enlace que le llega por email. --timeout N: cierra la
    # escucha tras N segundos si nadie autoriza (ventana del email del vigilante).
    escuchar = "--escuchar" in sys.argv
    timeout_s = 0
    if "--timeout" in sys.argv:
        i = sys.argv.index("--timeout")
        if i + 1 < len(sys.argv):
            try:
                timeout_s = int(sys.argv[i + 1])
            except ValueError:
                timeout_s = 0

    s = load_settings()
    if not (s.schwab_app_key and s.schwab_app_secret):
        print("Faltan SCHWAB_APP_KEY / SCHWAB_APP_SECRET en API/.env.")
        return 1

    parsed = urlparse(s.schwab_callback_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 443

    schwab = SchwabProvider(
        s.schwab_app_key, s.schwab_app_secret, s.schwab_callback_url, s.schwab_token_path,
    )

    cert_path, key_path = _self_signed_cert()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    try:
        httpd = HTTPServer((host, port), _make_handler(schwab))
    except PermissionError:
        print(f"No pude abrir el puerto {port}. Prueba con permisos de admin.")
        return 1
    except OSError as e:
        print(f"No pude abrir {host}:{port} ({e}). ¿Otro proceso lo usa?")
        return 1
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    url = schwab.authorize_url()
    if escuchar:
        # Modo email: el usuario clicará el enlace desde su correo. Solo
        # escuchamos; opcionalmente cerramos la ventana tras timeout_s.
        if timeout_s > 0:
            def _deadline() -> None:
                time.sleep(timeout_s)
                if "status" not in _RESULT:
                    threading.Thread(target=httpd.shutdown, daemon=True).start()
            threading.Thread(target=_deadline, daemon=True).start()
        print(f"Escuchando en {host}:{port} la redirección de Schwab "
              f"(ventana {timeout_s or '∞'} s). No abro navegador: "
              "el usuario clicará el enlace del email.")
    else:
        print("Abriendo el navegador para el login de Schwab…")
        print("Si no se abre solo, abre esta URL manualmente:\n" + url)
        print("\nTras autorizar, el navegador mostrará un AVISO DE SEGURIDAD en")
        print("127.0.0.1: haz clic en 'Avanzado' -> 'Continuar a 127.0.0.1'.")
        print("Esperando la redirección de Schwab…\n")
        webbrowser.open(url)

    httpd.serve_forever()  # sale cuando el handler llama shutdown() o vence el timeout
    status = _RESULT.get("status")
    if status == "ok":
        print("EXITO: Schwab autorizado. Tokens guardados. available =", schwab.available)
        return 0
    print("No se completó la autorización.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
