# Escuela — Tus clases de opciones e inversión

Aquí estudias tus clases de la bolsa de NY con el agente **`estudio`**. Tú dejas el material,
él te enseña, te resume, te toma examen y te pone a practicar.

## Cómo se usa (fácil)

1. Deja el material de tu clase en la carpeta correcta (ver abajo).
2. En el chat, dile algo como:
   - *"Estudia conmigo la clase de las griegas"*
   - *"Hazme un resumen de la clase de spreads"*
   - *"Tómame un examen de lo que vimos de calls y puts"*
   - *"Ponme a practicar con un caso real"*

No necesitas escribir comandos. Solo pídelo con tus palabras.

## 📍 Estado actual (2026-07-24)

- **10 clases archivadas y resumidas ✅** — abre `Notas de estudio/_INDICE.md` (o
  doble clic en **"Mis Resumenes de Clase"** en tu escritorio).
- **Playbook de 3 estrategias listo** para practicar en demo (`Estrategias/`, o
  doble clic en **"Mis Estrategias"**).
- **Registro de demo** montado para medir qué funciona.

## Dónde va cada cosa

| Carpeta | Qué va aquí |
|---|---|
| `Materiales/clases/` | **Tus clases originales** (PDFs) y su texto extraído en `clases/texto/`. La fuente que el agente lee. |
| `Materiales/` | Apuntes y notas de marco (ej. la curva semanal del VS3D, Gann). |
| `Notas de estudio/` | Los **resúmenes** de cada clase, para repasar. Empieza por `_INDICE.md`. |
| `Estrategias/` | El **playbook** (estrategias derivadas de tus clases) y el **registro de demo**. |
| `Examenes/` | Aquí el agente **te deja** los exámenes y tus resultados. |
| `Materiales/Pendiente de transcribir/` | Audios/videos que aún no son texto (ver abajo). |

## Accesos rápidos en tu escritorio (doble clic)
- **"Mis Resumenes de Clase"** → abre `Notas de estudio/`
- **"Mis Estrategias"** → abre `Estrategias/`

## Sobre los audios y videos

El agente lee texto, no escucha ni ve. Para usar una clase en audio o video hay que
convertirla a texto (transcripción). **Ya tienes una herramienta instalada para eso**, y es
privada: todo corre en tu PC, nada se sube a internet.

### Cómo transcribir (doble clic)

Dos formas, la que te sea más cómoda:

- **Arrastrar**: toma tu archivo de audio/video y **suéltalo encima de
  `Transcribir clase.bat`** (está en esta carpeta `Escuela/`). Se abre una ventanita, hace su
  trabajo y guarda el texto.
- **Por lotes**: deja uno o varios archivos en `Materiales/Pendiente de transcribir/` y haz
  **doble clic en `Transcribir clase.bat`**. Transcribe todos.

El texto queda en `Materiales/` como `NOMBRE - transcripcion.txt` (y otra versión con marcas
de tiempo). Con eso ya puedes decirle a Claude: *"estudia conmigo esta clase"*.

> La primera transcripción ya bajó el modelo de idioma, así que de aquí en adelante es rápido.
> Si alguna clase queda con palabras mal entendidas, dime y subimos la precisión (modelo
> `medium`, más lento pero más exacto).

**Alternativa YouTube**: si la clase es un video de YouTube, muchas veces ya trae
transcripción automática — ábrela, cópiala y pégala aquí o guárdala en `Materiales/`.

## Los cuatro modos del agente

1. **Estudiar** — te explica y te va preguntando para que entiendas de verdad.
2. **Resumir** — te deja un resumen con fichas de repaso.
3. **Evaluar** — te toma examen y te corrige explicando el porqué.
4. **Ejecutar** — te pone a aplicar lo aprendido en un caso real (como práctica, nunca como
   consejo de inversión).
