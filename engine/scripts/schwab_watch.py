"""Vigilante de la autorizacion de Schwab — avisa ANTES de que venza.

El refresh token de Schwab muere a los ~7 dias. Cuando muere, el precio en
vivo se pierde y el monitoreo de posiciones queda ciego. Este script corre a
diario, mira cuanta vida le queda a la autorizacion, y manda email de aviso
mientras todavia hay tiempo de renovar — en vez de enterarse cuando ya fallo.

No toca credenciales ni puede renovar solo: el login es de Tania, en Schwab.
Solo avisa.

Uso:
    python scripts/schwab_watch.py           # revisa y avisa si toca
    python scripts/schwab_watch.py --forzar  # manda el email igual (prueba)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from monitor_posiciones import enviar_email  # noqa: E402
from wbj.config import load_settings  # noqa: E402
from wbj.providers.schwab import SchwabProvider  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
POSICIONES = REPO / "API" / "posiciones.json"

REFRESH_TTL_DAYS = 7.0   # limite de Schwab, no nuestro.
AVISAR_BAJO_DIAS = 2.0   # avisar cuando queden 2 dias o menos.
VENTANA_ESCUCHA_SEG = 6 * 3600  # el atrapador escucha 6h tras el email (11 AM–5 PM).


def _link_login() -> str:
    """URL de login de Schwab para el boton del email. Lleva el client_id
    publico (igual que la barra del navegador), nunca el secret."""
    s = load_settings()
    prov = SchwabProvider(
        s.schwab_app_key, s.schwab_app_secret,
        s.schwab_callback_url, s.schwab_token_path,
    )
    return prov.authorize_url()


def _arrancar_atrapador(segundos: int = VENTANA_ESCUCHA_SEG) -> bool:
    """Lanza schwab_catch.py en modo escucha, desligado e invisible, para
    atrapar el codigo cuando Tania clique el enlace del email. Si el puerto ya
    esta ocupado (otro atrapador vivo) el hijo sale solo — sin ruido."""
    script = Path(__file__).resolve().parent / "schwab_catch.py"
    flags = 0
    if os.name == "nt":  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        flags = 0x00000008 | 0x00000200
    try:
        subprocess.Popen(
            [sys.executable, str(script), "--escuchar", "--timeout", str(segundos)],
            creationflags=flags, close_fds=True,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:  # noqa: BLE001
        return False


def _destino() -> str:
    try:
        cfg = json.loads(POSICIONES.read_text(encoding="utf-8"))
        return cfg.get("email_destino", "")
    except (OSError, json.JSONDecodeError):
        return ""


def estado() -> dict:
    """Vida restante de la autorizacion. Nunca imprime ni devuelve secretos."""
    s = load_settings()
    path = s.schwab_token_path
    if not path.exists():
        return {"situacion": "sin_autorizar", "dias_restantes": 0.0}
    try:
        tokens = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"situacion": "ilegible", "dias_restantes": 0.0}

    saved = tokens.get("refresh_saved_at")
    if not saved:
        return {"situacion": "ilegible", "dias_restantes": 0.0}

    dias_usados = (time.time() - float(saved)) / 86400.0
    restantes = REFRESH_TTL_DAYS - dias_usados
    vence = datetime.fromtimestamp(float(saved)) + timedelta(days=REFRESH_TTL_DAYS)
    return {
        "situacion": "vencido" if restantes <= 0 else "vivo",
        "dias_restantes": restantes,
        "autorizado_el": datetime.fromtimestamp(float(saved)).strftime("%d-%b-%Y %H:%M"),
        "vence_el": vence.strftime("%d-%b-%Y a las %H:%M"),
    }


def main() -> int:
    forzar = "--forzar" in sys.argv
    e = estado()
    sit = e["situacion"]
    dias = e["dias_restantes"]

    if sit == "vivo":
        print(f"Schwab OK — quedan {dias:.1f} dias (vence {e['vence_el']}).")
    else:
        print(f"Schwab {sit.upper()} — hay que renovar.")

    urgente = sit != "vivo" or dias <= AVISAR_BAJO_DIAS
    if not (urgente or forzar):
        return 0

    # Arranca el atrapador ESCUCHANDO para que Tania renueve con un clic desde
    # el email (sin tocar carpetas). Si falla, el boton del Escritorio sigue de
    # respaldo — por eso el email lo menciona igual.
    link = _link_login()
    arrancado = _arrancar_atrapador()

    if sit == "vivo":
        asunto = f"Schwab vence en {dias:.0f} dia(s) — renueva para no perder el precio en vivo"
        intro = (f"Tu autorizacion de Charles Schwab vence el {e['vence_el']} "
                 f"(quedan {dias:.1f} dias).")
    else:
        asunto = "Schwab VENCIDO — el monitoreo de tus posiciones esta ciego"
        intro = ("La autorizacion de Charles Schwab ya no sirve: ahora mismo NO "
                 "hay precio en vivo y el monitor de tus posiciones esta ciego.")

    cuerpo = (
        f"{intro}\n\n"
        "RENUEVA DESDE AQUI (haz clic en este enlace):\n"
        f"  {link}\n\n"
        "Inicia sesion en Schwab y autoriza. Al volver a 127.0.0.1 sale la\n"
        "pantalla 'Your connection isn't private': el codigo caduca en 30\n"
        "SEGUNDOS. No la leas. Dos clics seguidos:\n"
        "   Advanced  ->  Continue to 127.0.0.1 (unsafe).\n\n"
        "RESPALDO: si pasaron mas de 2 horas desde este correo, usa el boton\n"
        "'Renovar Schwab' de tu Escritorio (hace exactamente lo mismo)."
    )
    boton_html = (
        "<div style=\"font-family:system-ui,Arial,sans-serif;max-width:560px;"
        "line-height:1.55;color:#16181d\">"
        f"<p style='font-size:15px'>{intro}</p>"
        f"<a href=\"{link}\" style=\"display:inline-block;background:#00a0df;"
        "color:#fff;font-size:17px;font-weight:700;padding:15px 30px;"
        "border-radius:11px;text-decoration:none;margin:8px 0 4px\">"
        "Renovar Schwab ahora &rarr;</a>"
        "<p style='background:#fef4e2;border-radius:9px;padding:12px 16px;"
        "font-size:13px;color:#7a5b16'><b>OJO:</b> al volver a <b>127.0.0.1</b> "
        "sale &ldquo;Your connection isn&rsquo;t private&rdquo;. El c&oacute;digo "
        "caduca en <b>30 segundos</b> &mdash; no la leas, dos clics seguidos: "
        "<b>Advanced &rarr; Continue to 127.0.0.1</b>.</p>"
        "<p style='font-size:12px;color:#777'>Si el bot&oacute;n no completa "
        "(pasaron m&aacute;s de 2h desde este correo), usa el bot&oacute;n "
        "&ldquo;Renovar Schwab&rdquo; de tu Escritorio.</p></div>"
    )
    if not arrancado:
        # No pudimos dejar el atrapador escuchando: el clic del email quedaria a
        # medias, asi que empujamos el respaldo del Escritorio como via principal.
        cuerpo = ("[Nota: usa el boton 'Renovar Schwab' de tu Escritorio para "
                  "esta renovacion.]\n\n") + cuerpo

    print(enviar_email(f"Warren Buffett Jr — {asunto}", cuerpo, _destino(), html=boton_html))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
