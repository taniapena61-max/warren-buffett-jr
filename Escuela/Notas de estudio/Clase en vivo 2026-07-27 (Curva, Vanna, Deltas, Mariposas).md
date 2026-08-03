# 🎥 Clase en vivo — 2026-07-27 (Latino Wall Street) · resumen

> Sesión en vivo de ~72 min. Transcrita local con faster-whisper (modelo "small",
> video a 1.5x) → hay **errores de ASR** (Vanna aparece como "Banna", Fed como "afet",
> algún número suelto). Para datos exactos, ver el video o pedir re-transcripción
> "medium". Transcripción: `Materiales/clases/texto/Clase en vivo 2026-07-27 - Curva,
> Vanna, Deltas y Mariposas.txt`.

## De qué trató
Repaso vivo del **método de la curva del SPX** con foco en **PUTs OTM, Vanna y la
lectura de deltas**, más aplicación a **verticales y mariposas**.

## Puntos clave
1. **La curva es ASIMÉTRICA (skew).** Se lee a través de los **PUTs OTM**: ahí está
   la mayor exposición institucional y **es lo que de verdad mueve el SPX** (los fondos
   entran por los puts OTM).
2. **Los deltas son zonas recurrentes de soporte/resistencia.** El precio hace
   "ping-pong" en el **delta 0.25**; los **.25 / .16 / .15** coinciden con zonas que ya
   fueron importantes. Los **deltas del viernes de la próxima semana se leen desde el
   lunes** (se toman temprano).
3. **Vanna** (repaso): la vol mueve el delta; el rally sin compradores. Comentan la
   **caída rápida de volatilidad** (crush) del día.
4. **Venta en el .25:** vender el strike **0.25** (ej. 7450) o **un poco más adentro
   por la prima**. Verticales del mismo día.
5. **Mariposas:** se abren **según el día**, típicamente **desde las ~11 AM**; ojo:
   *"no entras vendiendo la mariposa"* (hay un matiz de timing en la entrada). **La
   próxima semana profundizan en mariposas.**
6. **Comprar PUT cuando la vol sube** (VIX ~20) esperando que el precio siga bajando
   (jugada direccional con vol).
7. **Bear call / broken wing desde una resistencia.**

## Cómo corrobora lo que ya tenemos (nuestro sistema)
- **PUTs OTM + skew** → refuerza [[La Curva del SPX]] y el **Put Wall**.
- **Deltas recurrentes (.25/.16/.15)** → **valida** lo que agregamos hoy: leer los
  **deltas de la cadena** (`rango_por_delta`) y los "deltas de apertura". Tania tenía
  razón en que hay que buscarlos.
- **Mariposa = 0DTE, timing desde ~11 AM, no entrar solo vendiendo** → coincide con la
  **ruta 0DTE** (dealer/charm: el charm empuja en la 2ª mitad de la sesión) y con que
  el 0DTE se lee con gamma/charm/straddle, no con las 3 confluencias.
- **Crush de vol** → coincide con que en 0DTE **el crush es salida**.

## 🔬 Profundización (lo NUEVO para nuestras entradas)

### 1. La pregunta que va PRIMERO: ¿qué griego voy a poner a trabajar?
Antes de abrir nada, decide **cuál griego te va a pagar** — ahí está tu ventaja:
- **Movimiento → GAMMA** (te alejas del ATM).
- **Volatilidad → VANNA/vega** (dependes de que la vol se mueva).
- **Tiempo → THETA/CHARM** (que pase el tiempo con el precio quieto).

Mapa por estrategia (de la clase):
- **Mariposa ATM = TIEMPO (theta).** Abres ATM y "solo haces que pase el tiempo"; el
  precio se queda en la zona y recolectas por theta.
- **Broken wing / bear call desde una resistencia = sobre todo THETA + CHARM** (algo de
  gamma). No necesitas gran desplazamiento; necesitas que pase el tiempo y que el precio
  quede bajo tu strike.
- **Reversal = VOLATILIDAD (Vanna) + gamma.** **Manda la vol, NO el delta 0.25.** Si no
  tienes la vol a favor, no tienes la ventaja → no hay reversal.

### 2. El RELOJ intradía (clave para la mariposa 0DTE)
- **Mañana (apertura–~11 AM): manda VANNA / los picos de volatilidad** más fuertes. **NO
  entrar la mariposa aquí.**
- **11 AM – 1 PM: VENTANA de la mariposa.** Manda **theta**; menor probabilidad de
  movimientos bruscos; buscas que el precio **se quede en la zona** (ATM).
- **Después de la 1 PM: el CHARM activa el GAMMA** → los dealers se activan a neutralizar →
  **movimientos erráticos de la tarde.** Riesgo para la mariposa.
- **Viernes (vencimientos semanales): mayor sensibilidad del charm.**
- Regla del profe: *"abran la mariposa desde las 11 AM hasta la 1 PM"*, y **nunca entrar
  vendiendo mariposa con la vol picando** (VIX por encima de ~18 / haciendo picos = poco
  favorable). La mariposa quiere **calma**.

### 3. El MECANISMO del crush (por qué pasa — y la trampa que hay que desaprender)
- El crush ocurre por el **cierre de los PUTs OTM que se volvieron ATM.** Secuencia: puts
  0.25/0.15 delta → el precio cae hacia ellos → se vuelven 0.50/0.60 ATM → quien los vendió
  **cierra esas coberturas** → **la vol cae (crush)** y el precio se recupera.
- **Trampa a desaprender:** *"compro un put porque la vol sube / se rompe un nivel"* = MAL.
  Que la vol pique y el precio baje a los puts **NO significa que seguirá cayendo** — la
  cola izquierda cumplió su función, se cierra, **viene el crush** (vol abajo + rebote).
  Por eso en 0DTE **el crush es salida/recompra, no razón para perseguir la baja.**

### 4. Ejemplo de la clase (Gann + delta)
- Trade "de puro delta": aprovechar el desplazamiento **7435 → 7500** (~70 pts).
- **Gann:** *miércoles 29-jul en 180°*, con niveles **~7400 y ~7565**. Cerrar **antes del
  viernes** (evitar los eventos/OpEx). Practicar en demo.

## Para practicar / repasar
- Pídeme *"examíname de esta clase"* o *"profundiza en las mariposas de esta clase"*.
- Cuando la próxima semana den la clase de mariposas, la grabamos y transcribimos igual.
