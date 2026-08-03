# 🎥 VolSignals — Delta, Gamma, Theta (webinar bottom-up) · qué es nuevo

> Webinar de VolSignals (Dan, ex-MM) enseñando los griegos desde cero. Transcripción en
> `Materiales/clases/texto/`. **Veredicto: ~80% ya lo teníamos; abajo lo NUEVO.**

## Ya lo teníamos (repaso, no agregar)
- Delta = lo que se hedgea; call/put; **hard delta** (deep ITM, ~±1) vs **soft delta** (OTM).
- **Gamma = velocidad/convexidad**; 0DTE = más gamma; largo plazo = menos. Elegir gamma
  por convexidad al movimiento, Vega por IV. (Ya en [[griegos-reloj-intradia-0dte]].)
- **Theta = costo del negocio**; más IV = más theta; acelera cerca del vencimiento; 0DTE
  decae brutal (por eso "retail sufre"). (Ya lo teníamos.)
- MM hedgea rígido por modelo; el impacto que importa es el **dinámico** (gamma/charm/vanna)
  tras el hedge inicial de delta. **Posición > flujo** (el flujo es impredecible). (Ya.)

## 🆕 LO NUEVO (vale la pena)

### 1. ⭐ Decaimiento de tiempo VARIABLE / "vol-time" (lo más útil)
El MM **no decae el straddle linealmente**. Decae **cuando hay actividad**: mucho en los
**primeros 30 min y últimos 30 min**; **poco al mediodía** (todos almorzando). Refina
nuestro **reloj intradía**.

### 2. ⭐ Decaimiento por EVENTO (refina el crush)
Alrededor de **FOMC / CPI / NFP**, el modelo **no mueve el tiempo hasta que ocurre el
evento**; entonces sale un **bloque comprimido de variance de golpe**. Por eso el **straddle
0DTE puede SUBIR hacia el evento** (ej. hacia la conferencia de Powell) y **colapsar
después = el crush**. → En días de evento, el 0DTE se juega por el evento: straddle
firme/arriba antes, **crush después**. Conecta con nuestro catalizador [[catalizadores-macro-fedwatch]].

### 3. El "efecto VIX de fin de semana" es un ARTEFACTO
El VIX usa **días calendario**; el MM usa **días de trading**. De viernes a lunes NO pasó
tiempo real (~1 min en su modelo), pero el VIX cuenta 2 días → parece que la IV baja. **No
es real** — no te dejes engañar por el VIX del lunes por la mañana.

### 4. Duración = tradeoff de griego
**Corto DTE → gamma / vol realizada**; **largo DTE → Vega / vol implícita**. El "sweet
spot" histórico ~30 días. Elegir según qué apuestas (movimiento de hoy vs cambio del
surface).

## 📚 Libros que recomienda (referencia de estudio)
1. **Natenberg — "Option Volatility & Pricing"** (el primer libro de la industria).
2. **Colin Bennett — "Trading Volatility"** (siguiente nivel, mundo real).
3. **Taleb — "Dynamic Hedging"** (avanzado; solo con experiencia).
