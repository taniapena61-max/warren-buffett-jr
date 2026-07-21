"""Lector Gmail de SOLO LECTURA vía IMAP — para cazar alertas de MarketSnack.

Se conecta a Gmail con una *contraseña de aplicación* de Google (no la
contraseña normal de la cuenta), busca los correos de un remitente concreto
(p. ej. MarketSnack) y devuelve su texto plano. Nunca borra, nunca marca,
nunca envía: abre la conexión en modo readonly y solo lee.

Credenciales desde `API/.env`:
    GMAIL_ADDRESS         la dirección (taniapena61@gmail.com)
    GMAIL_APP_PASSWORD    contraseña de aplicación de Google (16 caracteres)
    MARKETSNACK_SENDER    (opcional) filtro de remitente; si falta, se busca
                          por la palabra "marketsnack" en remitente/asunto.

Diseño defensivo: cualquier fallo de red/login se reporta como error, nunca
tumba al que lo llama.
"""

from __future__ import annotations

import email
import imaplib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.header import decode_header
from email.utils import parsedate_to_datetime

_IMAP_HOST = "imap.gmail.com"
_IMAP_PORT = 993


@dataclass
class Mensaje:
    """Un correo leído: remitente, asunto, fecha y texto plano."""
    remitente: str
    asunto: str
    fecha: datetime | None
    texto: str


def _decodificar(valor: str | None) -> str:
    if not valor:
        return ""
    partes = decode_header(valor)
    out = []
    for txt, enc in partes:
        if isinstance(txt, bytes):
            out.append(txt.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(txt)
    return "".join(out)


def _texto_plano(msg: email.message.Message) -> str:
    """Extrae el cuerpo en texto plano; cae a HTML crudo despojado si hace falta."""
    if msg.is_multipart():
        # preferir text/plain
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and \
                    "attachment" not in str(part.get("Content-Disposition", "")):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8",
                                          errors="replace")
        # sin text/plain: tomar el primer text/html y quitar etiquetas
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(part.get_content_charset() or "utf-8",
                                          errors="replace")
                    return re.sub(r"<[^>]+>", " ", html)
        return ""
    payload = msg.get_payload(decode=True)
    if payload:
        txt = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
        if msg.get_content_type() == "text/html":
            return re.sub(r"<[^>]+>", " ", txt)
        return txt
    return ""


def leer_marketsnack(direccion: str, app_password: str,
                     remitente: str | None = None,
                     dias: int = 7, limite: int = 10) -> dict:
    """Devuelve los correos recientes de MarketSnack (o remitente dado).

    Returns {"mensajes": [Mensaje,...]} o {"error": "..."}.
    Solo lectura: EXAMINE (readonly), sin marcar como leído.
    """
    if not direccion or not app_password:
        return {"error": "faltan GMAIL_ADDRESS o GMAIL_APP_PASSWORD en API/.env"}

    try:
        M = imaplib.IMAP4_SSL(_IMAP_HOST, _IMAP_PORT)
    except OSError as e:
        return {"error": f"no se pudo conectar a Gmail: {type(e).__name__}"}

    try:
        try:
            M.login(direccion, app_password)
        except imaplib.IMAP4.error:
            return {"error": "login rechazado — revisa la contraseña de aplicación "
                             "(y que la verificación en 2 pasos esté activa)"}
        M.select("INBOX", readonly=True)  # readonly: nunca modifica nada

        desde = (datetime.now() - timedelta(days=dias)).strftime("%d-%b-%Y")
        if remitente:
            criterio = ["FROM", remitente, "SINCE", desde]
        else:
            criterio = ["SINCE", desde]  # filtramos por texto abajo
        typ, data = M.search(None, *criterio)
        if typ != "OK":
            return {"error": "la búsqueda IMAP falló"}

        ids = data[0].split()
        ids = ids[-limite * 3:] if not remitente else ids[-limite:]

        mensajes: list[Mensaje] = []
        for mid in reversed(ids):
            typ, raw = M.fetch(mid, "(RFC822)")
            if typ != "OK" or not raw or not raw[0]:
                continue
            msg = email.message_from_bytes(raw[0][1])
            frm = _decodificar(msg.get("From"))
            asunto = _decodificar(msg.get("Subject"))
            if not remitente:  # filtro por palabra clave
                if "marketsnack" not in (frm + asunto).lower():
                    continue
            try:
                fecha = parsedate_to_datetime(msg.get("Date"))
            except (TypeError, ValueError):
                fecha = None
            mensajes.append(Mensaje(frm, asunto, fecha, _texto_plano(msg)))
            if len(mensajes) >= limite:
                break
        return {"mensajes": mensajes}
    finally:
        try:
            M.logout()
        except Exception:  # noqa: BLE001
            pass


def remitentes_recientes(direccion: str, app_password: str, dias: int = 7,
                         limite: int = 40) -> dict:
    """Lista los remitentes recientes — para identificar cuál es MarketSnack."""
    if not direccion or not app_password:
        return {"error": "faltan credenciales de Gmail en API/.env"}
    try:
        M = imaplib.IMAP4_SSL(_IMAP_HOST, _IMAP_PORT)
        try:
            M.login(direccion, app_password)
        except imaplib.IMAP4.error:
            return {"error": "login rechazado — revisa la contraseña de aplicación"}
        M.select("INBOX", readonly=True)
        desde = (datetime.now() - timedelta(days=dias)).strftime("%d-%b-%Y")
        typ, data = M.search(None, "SINCE", desde)
        vistos: dict[str, str] = {}
        for mid in reversed(data[0].split()[-limite:]):
            typ, raw = M.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            if typ != "OK" or not raw or not raw[0]:
                continue
            hdr = email.message_from_bytes(raw[0][1])
            frm = _decodificar(hdr.get("From"))
            if frm and frm not in vistos:
                vistos[frm] = _decodificar(hdr.get("Subject"))
        return {"remitentes": vistos}
    except OSError as e:
        return {"error": f"no se pudo conectar: {type(e).__name__}"}
    finally:
        try:
            M.logout()
        except Exception:  # noqa: BLE001
            pass
