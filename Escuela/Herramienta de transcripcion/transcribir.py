# -*- coding: utf-8 -*-
"""
Transcriptor local de clases — Warren Buffett Jr / Escuela
Convierte audios y videos a texto usando faster-whisper. Todo corre en la PC de Tania;
nada se sube a internet (solo la primera vez descarga el modelo de idioma).

Uso:
  - Doble clic en "Transcribir clase.bat", o
  - Arrastrar un archivo de audio/video encima del .bat, o
  - python transcribir.py "ruta\\del\\audio.mp3"

Si no se pasa ningún archivo, transcribe todo lo que haya en
"Escuela/Materiales/Pendiente de transcribir/".
"""

import sys
import os
from pathlib import Path

# --- Rutas del proyecto -------------------------------------------------------
AQUI = Path(__file__).resolve().parent
ESCUELA = AQUI.parent
MATERIALES = ESCUELA / "Materiales"
PENDIENTES = MATERIALES / "Pendiente de transcribir"

# Formatos que sabemos leer (av/ffmpeg incluido en faster-whisper los decodifica).
EXT_VALIDAS = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus", ".wma", ".flac",
               ".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".ts"}

# Modelo por defecto. "small" = buen balance de precisión y velocidad en CPU.
# Para máxima precisión (más lento) cambiar a "medium".
MODELO = os.environ.get("WHISPER_MODELO", "small")
IDIOMA = os.environ.get("WHISPER_IDIOMA", "es")


def log(msg=""):
    print(msg, flush=True)


def juntar_archivos(args):
    """Decide qué archivos transcribir: los pasados por argumento, o la carpeta de pendientes."""
    archivos = []
    if args:
        for a in args:
            p = Path(a)
            if p.is_file():
                archivos.append(p)
            else:
                log(f"  ! No encuentro: {a}")
    else:
        if PENDIENTES.exists():
            for p in sorted(PENDIENTES.iterdir()):
                if p.is_file() and p.suffix.lower() in EXT_VALIDAS:
                    archivos.append(p)
    return archivos


def transcribir(modelo, ruta):
    """Transcribe un archivo y guarda un .txt junto a Materiales. Devuelve la ruta de salida."""
    log(f"\n=== Transcribiendo: {ruta.name} ===")
    log("  (procesando... esto puede tardar según el largo del audio)")

    segmentos, info = modelo.transcribe(
        str(ruta),
        language=IDIOMA,
        vad_filter=True,               # ignora silencios largos
        beam_size=5,
    )
    log(f"  Idioma detectado: {info.language}  |  duración: {info.duration:.0f}s")

    partes_texto = []
    partes_tiempo = []
    for seg in segmentos:
        texto = seg.text.strip()
        partes_texto.append(texto)
        ini = _mmss(seg.start)
        partes_tiempo.append(f"[{ini}] {texto}")
        log(f"  {ini}  {texto}")

    salida_txt = MATERIALES / f"{ruta.stem} - transcripcion.txt"
    salida_ts = MATERIALES / f"{ruta.stem} - transcripcion (con tiempos).txt"

    encabezado = (
        f"Transcripción de: {ruta.name}\n"
        f"Modelo: {MODELO}  |  Idioma: {info.language}  |  Duración: {info.duration:.0f}s\n"
        f"{'-' * 60}\n\n"
    )
    salida_txt.write_text(encabezado + " ".join(partes_texto) + "\n", encoding="utf-8")
    salida_ts.write_text(encabezado + "\n".join(partes_tiempo) + "\n", encoding="utf-8")
    return salida_txt


def _mmss(segundos):
    m = int(segundos // 60)
    s = int(segundos % 60)
    return f"{m:02d}:{s:02d}"


def main():
    args = sys.argv[1:]
    archivos = juntar_archivos(args)

    if not archivos:
        log("No hay nada que transcribir.")
        log(f"Deja tu audio/video en:\n  {PENDIENTES}")
        log("o arrastra el archivo encima de 'Transcribir clase.bat'.")
        return 1

    log(f"Archivos a transcribir: {len(archivos)}")
    log(f"Modelo: {MODELO} (idioma {IDIOMA})")
    log("Cargando el motor de transcripción...")
    log("  (la PRIMERA vez descarga el modelo de idioma, ~0.5 GB — solo pasa una vez)")

    from faster_whisper import WhisperModel
    modelo = WhisperModel(MODELO, device="cpu", compute_type="int8")

    generados = []
    for ruta in archivos:
        try:
            salida = transcribir(modelo, ruta)
            generados.append(salida)
            log(f"  -> Guardado: {salida.name}")
        except Exception as e:
            log(f"  ! Error con {ruta.name}: {e}")

    log("\n=========================================")
    if generados:
        log(f"Listo. {len(generados)} transcripción(es) en la carpeta Materiales:")
        for g in generados:
            log(f"  - {g.name}")
        log("\nYa puedes decirle a Claude: \"estudia conmigo esta clase\".")
    else:
        log("No se generó ninguna transcripción.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
