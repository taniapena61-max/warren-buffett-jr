# 🛰️ VS3D (VolSignals) — cómo leer la posición de los Market Makers

> Investigado de volsignals.com y su documentación (2026-07-25). VS3D = **VolSignals
> 3D**, plataforma creada **por market makers de carrera** de SPX.

## Qué lo hace especial (y por qué tu instinto es correcto)
La mayoría de las herramientas de gamma **ESTIMAN** la posición del dealer desde el
interés abierto + suposiciones (el método bid/ask que tu clase dice que **falla**).

**VS3D usa datos REALES de clearing de OCC y CBOE, clasificados por participante**
(customer buys, non-customer buys, firm sales, market maker sales). No estima:
**ve** dónde está largo y corto el market maker, por strike y vencimiento, en SPX y VIX.
Además **filtra el volumen MM-contra-MM** (el que infla el tape pero neta a cero).
Por eso es de las pocas que muestra posición real, no inferida.

## Cómo se lee (de su guía)
**Positions by Strike (barras horizontales):**
- 🟢 **Barra verde = MM neto LARGO.** Cubre vendiendo en subidas y comprando en
  caídas → **amortigua** (soporte implícito).
- 🔴 **Barra roja = MM neto CORTO.** Cubre comprando en subidas y vendiendo en
  caídas → **amplifica** (resistencia / gasolina).
- Línea punteada = precio actual (centro de gravedad).

**Gradient Chart (gradiente sobre las velas):**
- **Modo Gamma:** verde = gamma larga (contiene) · rojo = gamma corta (acelera).
- **Modo Charm:** verde = charm negativo (presión compradora con el tiempo) · rojo =
  charm positivo (presión vendedora cerca del vencimiento). Intensidad = tamaño.

**Position Grid / Calendar:** matriz strike × vencimiento; color más profundo =
posición más grande. El agregador de vencimientos marca qué fechas cargan más
posición (útil para rastrear rolos).

**Flujo de trabajo sugerido:** Gradient Chart (panorama) → strikes específicos →
grid (contexto de vencimiento) → calendario → dashboard propio.

## Otras herramientas parecidas (por si quieres comparar)
- **SpotGamma**, **MenthorQ**, **OptionsDepth**, **Tier1Alpha**, **SqueezeMetrics**
  (los del concepto original de GEX/DIX).
- ⚠️ Casi todas **estiman** desde interés abierto. VS3D es de las pocas con **datos
  de clearing por participante** — por eso es difícil de igualar para posición real.

## Recursos
- Web: volsignals.com · App: vs3d.volsignals.com
- **YouTube (inglés):** https://www.youtube.com/@VolSignals
  - "How Market Makers Actually Move Markets" · "SPX Option Hedging Moves Markets" · "Trading Futures with VS3D"

## Cómo aprender de sus videos (están en inglés)
Claude **no puede ver/oír videos.** Pero SÍ puede leer texto. El plan que ya tienes montado:
1. Descarga el video de VolSignals.
2. Pásalo por **`Transcribir clase.bat`** (tu herramienta local de transcripción).
3. Claude lee la transcripción, la **resume y te la traduce al español.**
Así conviertes sus clases en inglés en lecciones tuyas en español.
