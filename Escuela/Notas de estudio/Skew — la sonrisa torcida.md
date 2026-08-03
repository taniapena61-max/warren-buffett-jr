# 😬 Skew — la sonrisa torcida de la volatilidad

> Lo que el **precio del miedo** revela antes que el precio del activo.
> El skew es la antesala de Vanna: entender el skew es entender **por qué Vanna
> mueve al mercado en las caídas.** *(Ver [Vanna II](El%20Poder%20de%20Vanna%20II%20%28el%20mapa%20en%20VS3D%29.md).)*

## Una volatilidad por strike (el fin del mundo plano)
- Black-Scholes asume **una sola volatilidad** para todos los strikes. El mercado
  lo contradice: **cada strike cotiza su propia IV.**
- El **skew** es esa curva: cómo cambia la IV al recorrer los strikes.
- En índices, las **puts OTM cotizan IV más alta** que las calls OTM.
- **Idea madre:** la IV no es un número, es **una curva; y la curva tiene opinión.**

## 19 de octubre de 1987 — el día que nació el skew
- Antes del 87 la superficie era casi plana: el mercado creía en la campana de Gauss.
- El Lunes Negro cayó **−22.6% en un día** — un evento "imposible" según el modelo.
- Desde entonces las **puts OTM de índices nunca volvieron a ser baratas.**
- El skew es **la cicatriz**: la memoria del mercado escrita en precios. *Los modelos
  aprenden despacio; los precios, en un día.*

## Por qué existe — un mercado de seguros dentro del mercado
- **Demanda estructural:** las instituciones compran puts como seguro de cartera,
  siempre.
- **Oferta estructural:** venden calls contra sus acciones → abaratan el ala alcista.
- Los **dealers quedan cortos de puts** → cobran prima extra por cargar ese riesgo.
- Además: las **caídas son violentas y correlacionadas**; las subidas, lentas y
  ordenadas.
- **El skew = el equilibrio entre el miedo comprado y la codicia vendida.**

### El precio de las colas (la lectura de Taleb)
- Los retornos reales tienen **colas gordas.**
- Cuando el mercado cae, la IV sube → **correlación spot-vol negativa.**
- Una put OTM paga justo cuando todo lo demás falla: por eso cuesta cara.
- **No pagas por la probabilidad del evento, pagas por su consecuencia.**

## Cómo se mide — de la intuición al número
- Compara **IV a deltas iguales**: put 25Δ contra call 25Δ.
- **Risk Reversal (RR) = IV put 25Δ − IV call 25Δ** → en índices casi siempre positivo.
- Mide en **espacio de delta, no de strike** → así comparas entre vencimientos y activos.
- Sigue su historia: **el skew de hoy solo significa algo contra su propio rango**
  (no hay termómetro fijo/universal).

> Sin medida, "el skew está caro" es una opinión; con ella, es una señal.

### Las 3 coordenadas de la sonrisa (nivel, pendiente, curvatura)
De los mismos 3 puntos de la cadena salen 3 lecturas:
- **ATM** = el **nivel** → ¿cuánto se mueve?
- **Risk Reversal (RR)** = la **pendiente** (la resta) → ¿hacia dónde teme?
- **Butterfly (BF)** = la **curvatura** (el promedio contra el centro) → ¿temen
  sorpresa o dirección?

### Risk Reversal: doble vida (medida **y** operación)
- **Como operación:** compras la call 25Δ y la financias vendiendo la put 25Δ.
  En índices vendes el ala cara y compras la barata → **el skew te subsidia la dirección.**
- **Como medida:** pendiente pura de la sonrisa, sin nivel.
- **Lectura dinámica:** un RR que se **encarece con el mercado subiendo** = cobertura
  en la fortaleza (alguien grande se protege aunque suba).
- El RR es **inventario de riesgo de los dealers**; mantenerlo genera el flujo de Vanna.

## Empinado vs plano — dos regímenes, dos mensajes
- **Skew empinado:** protección demandada; el miedo **ya está pagado y en precio.**
- **Skew plano:** **complacencia** — nadie paga seguro, la cobertura brilla por su ausencia.
- ⚠️ **Giro contraintuitivo:** los cracks nacen **más veces del skew plano** que del
  empinado.
- **Skew que se empina en pleno rally** → alguien grande compra protección: toma nota.

> **El peligro no es el miedo caro, es la confianza barata.** El skew plano no es
> calma; es un mercado sin paracaídas puestos.

## Caso real — SPX, sesión del 29-jul-2026
Métrica Mixon 25Δ = (IV put 25Δ − IV call 25Δ) / IV ATM.
- El SPX cayó **−1.52%** y la protección entró **en la última vela**: cobertura
  reactiva al cierre.
- Los tres plazos saltaron: **1M → pctil 83 · 3M → pctil 88 · 6M → pctil 63.**
  La **panza (3M) lideró, el fondo (6M) confirmó** → demanda estructural, no un tic.
- Quien vendió esas puts fue el **MM**: hoy carga **inventario corto de skew fresco.**
- 🔑 **Skew pagado *tras* la caída no anticipa, reacciona;** y el que reacciona tarde
  paga percentil 88. *(El seguro grande vive en 3M, no en 0DTE.)*

> Esta sesión es la misma del **[FOMC 29-jul](Retrospectiva%202026-07-29%20%E2%80%94%20dia%20FOMC.md)**:
> el Put Wall gigante (imán durable) venció al pin, y aquí ves el otro lado del
> mismo evento — la protección entrando tarde y cara.

## Skew y dealer flow — la puerta de entrada a Vanna
- El skew implica que la **IV de cada strike se mueve cuando el spot se mueve.**
- Si el mercado cae, la IV sube → **las deltas cambian sin que el precio toque tu
  strike.**
- Los dealers recalibran coberturas por ese efecto: **eso es Vanna en acción.**
- Por eso el skew **no es una foto, es un motor**: alimenta los flujos del VS3D.

## Cómo se opera — cobrar el miedo de otros, con red
- **Verticales de puts con riesgo definido:** cobras prima engordada por el skew.
- **Ratio spreads y broken wings:** el ala cara financia la estructura.
- Comprar la put "cara" no es error **si compras consecuencia, no probabilidad.**
- 🏠 **Regla de la casa:** el skew **mejora tu precio de entrada, no sustituye tu
  tesis.** No operes el skew por sí solo; deja que el mercado te subsidie la estructura.

## Errores comunes (donde el skew cobra matrícula)
- ❌ Comparar IV a **strikes iguales** entre vencimientos distintos (peras con manzanas
  → usa espacio de delta).
- ❌ Leer skew empinado como **señal bajista automática**: a veces es solo seguro
  renovándose.
- ❌ Vender **puts desnudas** "porque están caras": caras por algo, y el algo llega.
- ❌ **Ignorar el skew** al armar spreads: pagas o cobras la pendiente sin saberlo.

> **El skew premia al que lo mide y le factura al que lo intuye.**

---
**Fuentes:** LWS · Taleb (colas gordas) · métrica Mixon 25Δ · datos SPX 29-jul-2026.
Material educativo, no es asesoramiento de inversión.
