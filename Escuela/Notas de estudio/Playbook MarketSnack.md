# Playbook de MarketSnack (MS) — cómo usarlo para entradas

> Consolidado por Claude a partir de los videos tutoriales de MarketSnack que Tania comparte.
> Fuente video 1: **"MarketSnack GEX Live Trading"** (Victor y Kevin, en vivo, SPX/XPX 0DTE).
> Se irá ampliando con cada video. Terminología de ellos + cómo se conecta con nuestro sistema.

---

## 1. Qué es el GEX (Gamma Exposure) — el corazón de MarketSnack

- Los **market makers (MM)** están obligados a cubrir (*hedge*) sus deltas constantemente.
- **Gamma** = "la delta de la delta": la aceleración/desaceleración con la que los MM cubren.
- El **GEX** mide esa exposición de gamma de los MM. NO es una herramienta de dirección: es una
  herramienta de **régimen** (cómo se va a comportar el precio).

## 2. La lente principal: gamma POSITIVA vs NEGATIVA (régimen, NO dirección)

> ⚠️ Regla que repiten sin parar: **positivo/negativo NO significa alcista/bajista.** Significa
> **tranquilidad (range-bound) vs volatilidad.** Sácate de la cabeza que negativo = bajista.

| | Gamma POSITIVA (+GEX) | Gamma NEGATIVA (−GEX) |
|---|---|---|
| Los MM cubren… | **CONTRA** la tendencia | **CON** la tendencia |
| Efecto | Calman el precio → **RANGE-BOUND** (rebota de soporte a resistencia) | **Amplifican** el movimiento → **VOLÁTIL** (más rápido, en cualquier dirección) |
| Cómo operar | **Comprar cada pullback** hacia el imán/green bar, rumbo al call wall | Cuidado: se mueve rápido en la dirección que va; no te pares enfrente |
| MM en resistencia | venden en resistencia (frenan) | agregan gasolina al fuego |

Ejemplo del video: el miércoles tuvieron **−21 mil millones** de gamma al cierre → el movimiento
a la baja fue **muy volátil**. Pero recalcan: pudo haber sido violento al alza igual. El signo
solo dice *qué tan violento*, no *hacia dónde*.

## 3. El GAMMA FLIP (la línea amarilla) — y la regla #1

- El **gamma flip** = el nivel que divide gamma positiva de negativa. En la tabla de GEX es la
  **línea amarilla**.
  - Precio **ARRIBA** de la línea amarilla → GEX **positivo**.
  - Precio **ABAJO** de la línea amarilla → GEX **negativo**.
- 🚫 **REGLA DE ORO: NO operes DENTRO de la zona del gamma flip.** Es choppy, hay "números
  cruzados", no da buena señal. *"I don't like to trade these ranges because you're in Gamma Flip
  Zone… stay away from that."*
- ✅ Se opera **ARRIBA o ABAJO** del flip, no encima. Ej. del video: "quieres entrar abajo de 420
  (te quitas el green bar) o arriba del gamma flip (~426); no te quedes atrapado en medio."

## 4. El IMÁN (Magnet) — el pin, y su RELOCALIZACIÓN

- El **imán** = el strike que atrae al precio (el pin del día). Se calcula **balanceando el open
  interest y el premium de ambos lados**: el strike más balanceado es el imán. (No dieron la
  fórmula exacta — la maneja su data scientist — pero es ese balance.)
- El precio **gravita hacia el imán**.
- 🔑 **Señal clave: la RELOCALIZACIÓN del imán.** Cuando el precio rompe el imán y este **se mueve
  al siguiente nivel**, confirma continuación. Si el precio sube pero **el imán NO se reubica**,
  hay que tener cuidado (puede ser falso). *"I want to see the magnet relocate… it hasn't
  relocated yet, that worries me."*
- En la página de la opción → info → **"magnet wall"** explica qué es.

## 5. Muros: PUT WALL (soporte) y CALL WALL (resistencia)

- **Put wall** = soporte (rebotaron en el put wall 7400).
- **Call wall** = resistencia / objetivo (apuntaban al call wall 7475).
- Zona de trade típica: **del put wall al call wall**. Ej.: "podemos operar de 450 a 475 (el call
  wall) después de romper esta zona."

## 6. Net GEX en $ (miles de millones) — el número en vivo

- Lo leen en vivo y cambia todo el día: fue **+25B → +7B → negativo → +15B** en una sesión.
- **+GEX alto y subiendo** (+15B, "puras barras verdes") = régimen sano para **comprar pullbacks**.
- Cruza el cero (va a negativo) = ojo, entra la volatilidad.
- *(Nota nuestra: es el mismo Net GEX que ya calculamos con `gex.py`; ver [[mvc-propio-independiente]].)*

## 7. Las GREEN BARS (barras verdes en los strikes)

- Barras verdes en un strike = **niveles de reacción / re-entrada**. El precio "salta" ahí, da
  rechazo, o sirve de soporte. *"425 green bar might be a good re-entry"*, *"we're jumping there
  because we have a green bar."*
- También sirven de aviso: si un green bar estorba en medio, mejor esperar a superarlo/perderlo.

## 8. Institutional Flow Tape (IFT) — leer el flujo que MUEVE la gamma

- El IFT muestra **los trades institucionales que ALIMENTAN la gamma** — un **algoritmo filtra**
  solo los relevantes (los que mueven el mercado / afectan la gamma), no todos. Por eso no ves
  cada trade: si el algoritmo no lo selecciona, no aparece.
- Son **trades ejecutados / hedges en tiempo real** (no órdenes).
- 🟢 **Señal: cuando VENDEN PUTS, es ALCISTA.** Ej.: vendieron $4.4M en puts 7500 → bullish; el
  "7450 bullish sell" al abrir marcó el sesgo. (Vender puts = apostar a que no bajará → alcista.)
- Puede no actualizarse por momentos: solo refleja cuando hay hedges nuevos que muevan la gamma.

## 9. Premium Exposure / Light Premium Exposure

- En los detalles del contrato: te dice **cuánto están arriba o abajo** los que tienen ese
  contrato abierto. Si el "light premium exposure" está por debajo del premium operado → **están
  perdiendo** en ese contrato.

## 10. PLAYBOOK de entrada (lo que hacen)

1. **Diagnostica el régimen primero** con el signo del GEX y el gamma flip (¿arriba o abajo de la
   línea amarilla?). Esto ANTES de elegir dirección. *(= nuestra regla "régimen primero".)*
2. **NO operes en la zona del flip** (choppy). Espera a estar claramente arriba o abajo.
3. **En gamma positiva:** compra **cada pullback** hacia el imán o un green bar, con objetivo el
   **call wall**. "Cada pullback es para comprar; sigue subiendo otra vez y otra vez."
4. **Confirma con la relocalización del imán** cuando rompe niveles.
5. **Usa el IFT** para ver dónde se posiciona el dinero grande (vender puts = alcista).
6. **Es un juego de espera** — no entres cada minuto. *"GEX is a waiting game."*
7. **Tamaño:** entran de a uno/dos contratos, promedian a la baja SOLO en swings (no en day
   trades). Ej. Amazon: compraron 27.50, agregaron ~17-18, promedio 23.50, vendieron 41.50/43
   (~100%). No sobre-operan; aguantan.

## 11. Advertencias / límites (de ellos)

- **GEX funciona mejor en ÍNDICES** (XPX/SPX, NDX, CBOE) con data en tiempo real. En acciones
  individuales es menos fiable porque **no se opera tanto premium en 0DTE**. (Se puede buscar GEX
  para cualquier acción, pero calibra distinto.)
- **Noticias grandes (Trump en vivo, earnings) → mercado calmo/choppy → NO operar.** "Don't try
  anything." *(= nuestra regla de días de evento / esperar la revalorización.)*
- **Blue Ocean para XPX a las 8:15 PM**: sesión extendida overnight del SPX (ahí recuperaron cuenta).

## 12. Cómo conecta con NUESTRO sistema

- El **imán** de ellos = nuestro **MVC** (`gex.py`); el **gamma flip** = nuestro `gamma_flip.py`;
  put/call wall = nuestros muros. **Ya lo calculamos solos** (ver [[mvc-propio-independiente]]).
- "Comprar el pullback hacia el imán" = tu estrategia de **[[estrategia-contraria-posicionarse-en-el-destino]]**
  (posicionarte EN el destino/imán), validada por ellos.
- "No operar la zona del flip" = **regla nueva y accionable** para nosotros.
- Sigue firme nuestro gatillo core: **volumen + confluencia de 3 lentes** ([[regla-volumen-obligatorio]]).
  El GEX de MS es una de esas lentes, no reemplaza el volumen.

---

---

# VIDEO 2 — "$25K Challenge Pt.5: GEX + Option Chain Intro" (la NUEVA actualización)

> Tutorial de la actualización nueva de MS: la **Option Chain** integrada con el GEX. Día de mucha
> volatilidad (FOMC + earnings MSFT/META). Mezcla español/inglés.

## A. La nueva OPTION CHAIN (lo más nuevo de MS)

- **Barra de búsqueda arriba**: escribe `SPX`, `NDX`, `NVDA`, `TSLA`… → te lleva a la Option Chain
  + Gamma Exposure de ese símbolo. (Dos formas de llegar al GEX: por la Option Chain o directo.)
- Por cada **strike** te muestra, sin tener que analizar profundo:
  - **Order book side**: % operado en el ask / bid / mid (ej. "44% ask, 42% bid, 13% mid").
  - **Asset premium sentiment**.
  - **Price pressure**: put wall, call wall, **magnet**, precio del activo.
  - **Expected drift**: hacia dónde se espera que se mueva. **Suele ir en la dirección del imán.** ⭐
  - **Money mix**: dónde se fue la mayoría del dinero (calls/puts, ITM, por vencimiento).
  - **Open interest change** para un vencimiento específico.
  - **Order structure**: % single-leg vs multi-leg (ej. "37% single / 63% multi"; también por strike).
  - **Notional**: dinero agregado ≈ **open interest × 100 × strike** (+ un algoritmo de gamma).
- **Clic en cualquier strike → detalle del contrato** (ask/bid/mid, mayor transacción, single/multi).
- **Vencimientos**: weeklies, monthly (ago/sep/oct/nov), quarterly = quad-witching (30-sep, 31-dic,
  31-mar, 30-jun-2027). Puedes **voltear** puts izq/der y ordenar strikes mayor↔menor.
- Funciona con **cualquier acción e índice**. Presumen: "la option chain más completa del mercado".

## B. GEX — leyenda de las líneas (importante para leer la gráfica)

| Línea | Qué es |
|---|---|
| **Gris** | el **imán** (magnet) |
| **Verde** | **call wall** |
| **Roja** | **put wall** (zona de GEX negativo) |
| **Naranja** | **gamma flip** (en el video 1 lo llamaron "amarilla"; es la línea del flip) |

- **Strikes mostrados**: 20 / 40 / 50 / 100 / 200. **Victor usa 40** (vista clara de dónde se
  concentran los strikes). El 200 es "medio freaky" (demasiado).
- **Gamma Ladder**: te dice los puntos más grandes del perfil. Puedes estar en un strike muy
  negativo Y tener un total negativo — son cosas distintas.
- Cada pestaña de **sesión** (Jul 29, 30, 31, Ago 3, 4…) trae su Net GEX, 1-day premium, OI y volumen.

## C. Regla del gamma flip, reforzada (lo dicen ~4 veces)

- **Abajo del flip → GEX negativo → más volatilidad →** cada rebote **tiende a venderse**; si el
  rebote NO se vende, el GEX negativo *aumenta* la volatilidad.
- **Arriba del flip → GEX positivo →** menos volatilidad, deriva más estable/alcista.
- **Net GEX cerca de CERO = el punto más pivotal** (lo vieron ir 10B→7B→2B; entre más cerca de
  cero, más decisivo el momento). ⭐

## D. Institutional Flow Tape (IFT) — a fondo

- Es un **"time & sales de opciones" filtrado por algoritmo**: solo los prints grandes (400k+),
  no los de $1,000. Solo lo que **alimenta la gamma**.
- **Filtra por strike**: escribe 7300 → ves solo ese strike; cuántos fueron **aggressive buy** vs
  **aggressive sell**.
- Cada print: hora, monto, strike, buy/sell, condición. **Clic → "C Chain"** te manda a la cadena
  del contrato. Los **puntos/círculos sobre los strikes = trades inusuales.**
- **Vender puts agresivo = normalmente ALCISTA** (lo repiten; compraron 7340 porque vendían puts
  en 7380/7385/7360).
- El **ETF/IFT tiene 15 min de retraso** para no-0DTE (en 0DTE ya cerró, no sirve el delay).
- Botón **"Resume/Resum Live"** = resumen de lo que pasó.

## E. TÁCTICAS NUEVAS de trading (video 2)

1. ⭐ **El truco de las 3:50 PM (cierre):** un solo market maker puede operar de **3:50 a 4:00 PM**;
   los demás deben cerrar/cubrir antes. Ese MM **entra a las 3:50 y "rebota" el precio** para
   rebalancear. → En GEX muy negativo al final del día, **espera el rebote de rebalanceo ~3:50**.
2. ⭐ **Flip soporte↔resistencia:** cuando el **put wall (soporte) se rompe, se voltea a
   resistencia** y el call wall/imán baja. Lo vieron en vivo: 7400 put wall rota → pasa a
   resistencia, imán cae a 7300. (Igual que un soporte roto que se vuelve techo en un gráfico.)
3. **En gamma negativa: espera el rebote.** "Cada rebote se vende, pero cazamos el rebote del put
   wall." No compres a media caída; espera el bote y opéralo.
4. **Paridad de instrumentos:** si operas **SPX** GEX → opera lo mismo en **ES** (futuro).
   **NASDAQ/NDX → NQ**. (SPX/ES misma cosa; el futuro va adelantado.)
5. **Expected drift → apunta al imán.** Úsalo como brújula de a dónde jala el día.
6. **Teoría del hedging (blackjack):** los MM son como la casa — mira cuánto "deben pagar" y a qué
   nivel tienen que ir para quedar *break-even en sus libros*; ahí jala el precio.

## F. Notas y límites (video 2)

- **GEX mejor en índices** (SPX/NDX, real-time). Para **acciones**, Victor mira los muros
  **mensuales** (no weekly) porque hay menos premium 0DTE.
- **Paciencia = core:** "no puedes estar operando cada 5 minutos; espera a romper tus call walls."
- Si no entiendes options/GEX → primero las clases base (ellos mismos lo recomiendan).
- (Negocio: plan $89; GEX gratis 7 días luego $99; +$10 para índices real-time sin delay de 15 min;
  anual $990; app móvil ~noviembre; API tal vez a futuro. No urgente para nosotros.)

## G. Cómo conecta con NUESTRO sistema (video 2)

- La **Option Chain** de MS = una versión más rica de tu **tabla Option Chain Statistics**
  ([[option-chain-statistics-tabla]]): put/call wall + magnet + expected drift ya masticados.
- El **"expected drift → imán"** refuerza tu **[[estrategia-contraria-posicionarse-en-el-destino]]**.
- El **flip soporte↔resistencia** y el **truco de las 3:50** son **nuevos y accionables** — vigilar
  esos en el diario de SPX ([[diario-spx-mercado]]).
- **Net GEX cerca de cero = pivote** → integrar como aviso en nuestro `gex.py`.
- Sigue firme: **volumen + 3 lentes** ([[regla-volumen-obligatorio]]); el GEX es una lente.

---

# TUTORIAL 1 — "MarketSnack Live Trading Tutorial" (la CONTRACT DETAILS PAGE)

> Sesión en vivo enfocada en **leer el flujo de un contrato individual** (no solo el GEX del índice).

## La Contract Details Page (clic en cualquier strike/contrato → 8 gráficas)

1. **Contract activity / price**: X = tiempo, Y = valor del contrato.
2. **Open Interest** (contratos abiertos).
3. **Volume** — ⭐ **clic en el pico de volumen → te lleva directo al Time & Sales** de ESE contrato
   (ya no hay que ir y venir al flow). Se puede ver por día / 5 días / mes / all-time.
4. **Open Premium** = **mark price × open interest** = dinero abierto en el contrato.
5. **Live Premium Exposure** — dos líneas: **azul = prima invertida/operada**, **dorada = valor
   vivo actual**.
   - Dorada **debajo** de la azul → los que tienen el contrato están **en pérdida** (ej. metieron
     $8.7M, vale $6.7M = −$2M).
   - Dorada **arriba** de la azul → están **ganando**. ⭐ Lee de un vistazo si el dinero grande va
     ganando o perdiendo en ese strike.
6. **Net Premium** = (ejecutado en el ASK) − (ejecutado en el BID).
   - **Positivo** → están **comprando** en la dirección de la etiqueta (calls = alcista).
   - **Negativo** → más ejecución en el bid (venta / dirección opuesta).
   - ⭐ Truco de entrada: cuando el net premium **brinca verde y luego regresa a cero/negativo** =
     **toma de ganancias** → buena pista de dónde entrar/salir.
7. **Option Pressure Index (OPI)** = % single-leg (azul) vs multi-leg (dorado). **Single-leg = más
   convicción y más fácil de leer.** Victor exige **75%+ single-leg** para fiarse. Multi-leg es más
   complejo (también da dirección, pero hay que analizarlo más). El OPI cambia según la ventana
   (día/5d/mes).

## Método de lectura para entrar (su forma en vivo)

- **Order book / sentiment**: cuando hay **gran discrepancia** (ej. 50 vs 43 bid/ask) → los MM van
  a **rebalancear**. Vigila ese desbalance.
- **Arma una escalera de strikes 0DTE**: calls a un lado, puts al otro; compara el **volumen
  agresivo** en cada strike. Donde **venden calls agresivo = techo del día** (resistencia). Donde
  **compran puts + venden calls = zona de reversión**.
- "The ladder up, the puts always go to the magnet" — los puts derivan hacia el imán.
- **No entrar a ciegas**: esperar a que el precio llegue al nivel, leer el flujo ahí, y entonces entrar.
- **Trades inusuales brillan en DORADO** en el flujo.

## Leer flujo institucional en LEAPs / largo plazo

- Prints grandes **single-leg** en opciones lejanas = **convicción institucional**. Ej.: NVDA
  "comprando" el equivalente a 30M acciones vía opciones a 5 años a $70 (2.1B notional) → "cuando
  la empresa más grande del mundo tiene convicción, es porque saben algo."
- **Enero** acumula mucho dinero (los LEAPs abren con 2-3 años de anticipación) → buenos strikes
  para ver dónde se posiciona el dinero grande.

## Conexión con lo tuyo
- La Contract Details Page es **justo para tus decisiones de LEAP** (MSFT, PLTR…): el **Live
  Premium Exposure** te dice si el dinero grande en ese strike gana o pierde, y el **OPI** si es
  convicción (single-leg) o estructura compleja. Úsalo antes de re-entrar. Ver [[option-chain-statistics-tabla]].

---

# TUTORIAL 2 — "MarketSnack Live Tutorial" (leer el FLUJO DE PRIMA + Contract Details 2.0)

> Tutorial DIDÁCTICO, previo al lanzamiento del GEX (ahí dicen "MarketSnack no tiene GEX todavía,
> sale en verano"). O sea: el **flujo de opciones es el core original**; el GEX vino después.

## Las BARRAS de agresividad (lo más visual y accionable)

Cada print del flow trae barras que dicen **DÓNDE se ejecutó**:
- **3 barras (rectángulo lleno + borde encendido) = lo MÁS agresivo** (arriba del ask = compra
  agresiva; abajo del bid = venta agresiva).
- 2 barras = medio agresivo · 1 barra = neutral (mid).
- ⭐ Victor/Kevin **solo cazan las de 3 barras** (agresivas). Hay leyenda en la plataforma.

## Reglas de lectura de prima (oro puro)

1. ⭐ **"La primera venta define la dirección."** La **primera venta grande del día** en un nombre
   marca el sesgo/techo. "Si lo venden primero, eso lo define — me encanta la primera venta." Ej.:
   Google 305 calls vendidos primero → no va a 305 (techo).
2. **Vender CALLS en un strike = ese strike es el TECHO** (tiene que quedar debajo). El sell más
   agresivo marca el nivel. Ej.: Oracle 180 calls vendidos → debe quedar arriba de 180 para ganar.
3. **Vender PUTS = alcista** (soporte). Delta **< .20 = venta de prima** (theta); .20+ = hedge.
4. **Yellow (live) DEBAJO de blue (traded) = el que tiene el contrato está PERDIENDO → oportunidad
   de entrar** ahí (si la tesis sigue y el OPI es alto). Yellow arriba = va ganando.
5. **Los strikes que quedan POSITIVOS todo el día = el soporte/resistencia del día.**
6. **Net premium**: brinca verde (compra) y luego regresa a negativo = **toma de ganancias / salida.**

## Las "rayitas" (conviction meter) — el gusto de Victor

MarketSnack calcula qué tan pegado a un lado quedó el print. **"1 rayita arriba / 1 abajo" (en el
medio, *en tierra*) NO le gusta** (poca convicción). Le gustan **2 o 3 rayitas** (claramente
agresivo). ⭐ El strike que queda "en tierra" (solo) suele ser **el nivel pivote a vigilar**.

## Volumen vs Open Interest — ¿posición nueva o cierre?

- **Volumen > Open Interest = contratos NUEVOS abriéndose** (alguien está construyendo posición →
  probablemente lo mantiene a mañana). ⭐
- Volumen < OI = mayormente cerrando.

## Criterio de SWING TRADE de Kevin (checklist)

single-leg · **agresivo (3 barras)** · ordenar por **premium** (los grandes) · **volumen > OI** ·
**delta ~.50** (ATM/ITM) · **OPI ≥ 80%** single-leg (≥90% mejor) · idealmente **60+ días** al vto.
→ Seguir el contrato en el **watchlist** y ver cómo el dinero grande acumula día a día (números
redondos = institucional).

## Otras piezas

- **Chart Studio**: comparar 2+ contratos lado a lado (calls vs puts a la vez), o enfocar 2 gráficas.
- **Sentiment/Feeling** (Contract Details 2.0): 2 algoritmos — cómo se comporta el MERCADO y cómo
  ese CONTRATO (bullish/bearish/neutral) en 30/5/1 días. Barras verdes=compra, rojas=venta.
- **Correlación (paridad):** si venden puts de QQQ (alcista) → puedes **longear NQ**; SPX↔ES.
- **No dejar expirar** (evita asignación); tomar 20%+ y salir. Excepción: Victor deja expirar
  0DTE de ÍNDICE (cash-settled, sin asignación). Ver [[fees-ejercicio-asignacion-brokers]].
- **Alertas**: agrega a watchlist → MS alerta solo; puedes poner price-target → **notificación por texto.**

## Conexión con lo tuyo
- Esto es tu **lente de flujo (MarketSnack)** a fondo: el tape que yo **jalo solo por cookie**. Con
  estas reglas puedo leerte **qué strikes son techo/piso** (primera venta, calls vendidos) y **dónde
  el dinero grande está atrapado** (yellow<blue) para tus entradas.
- "Vender puts = alcista / vender calls = techo" y "volumen > OI = posición nueva" = filtros
  directos para el `flujo` de `marketsnack.py`. Se pueden **codificar como señales**.

---

# TUTORIAL 3 — "MarketSnack Workshop LIVE" (el DASHBOARD y la rutina de entrada)

> Recorrido completo de la plataforma. Refuerza todo lo anterior; lo NUEVO clave es el **Dashboard**
> (la pantalla de inicio) y la **rutina con la que Victor arranca el día**.

## El DASHBOARD (pantalla de inicio) — por dónde EMPEZAR cada día

- **Market Sentiment**: % calls vs puts del mercado. ~56/44 = neutral. **≥60% calls → bullish
  (verde)** · **≥60% puts → bearish (rojo).**
- **Big Delta Trades**: los trades más grandes por delta.
- **Top performance by Open Interest change**: **cuánto OI se AGREGÓ** a cada acción (put o call).
  ⭐ Es donde está entrando dinero NUEVO — dice qué acciones investigar hoy.
- **Watchlist performance**: rendimiento de tu watchlist.
- **Top movers / low-cost contracts**: los contratos calientes del momento.
- Puedes traer el **flow feed a la watchlist y al dashboard** (sin entrar al flow feed aparte).

## ⭐ La RUTINA de Victor (cómo entra a la plataforma)

1. Mira el **Market Sentiment** del dashboard:
   - Si está **bullish/rich** → **busca CALLS**.
   - Si está **bearish** → **busca PUTS**.
2. Revisa el **Top OI change** → qué acciones tienen dinero nuevo entrando (y de qué lado).
3. Investiga esas acciones en el **flow feed** (filtros: single-leg, agresivo/3 barras, por premium).
4. Confirma en la **Contract Details** (net premium, live premium exposure yellow/blue, OPI ≥80%).
5. Cruza con el **GEX** (régimen: arriba/abajo del flip, imán, muros) para el timing.

## Conexión con lo tuyo
- El **Dashboard + Market Sentiment + Top OI change** es la forma rápida de **arrancar el día** y
  decidir el sesgo antes de mirar strikes. Encaja con tu "régimen primero".
- La rutina (sentiment → OI nuevo → flow → contract details → GEX) es un **embudo** que puedo
  replicar yo: sentiment y flow los jalo por cookie; GEX/imán/flip los calculo con `gex.py`. Solo
  el Market Sentiment y el OI-change habría que confirmarlos con captura tuya si los quieres exactos.

---

## RESUMEN — el método MarketSnack completo (5 videos)

**Embudo de decisión:** Dashboard (sentiment + OI nuevo) → Flow feed (single-leg agresivo, primera
venta define, vender puts=alcista/calls=techo) → Contract Details (yellow<blue=perdiendo, OPI≥80%,
vol>OI=posición nueva) → GEX (régimen +/−, gamma flip [NO operar su zona], imán y su relocalización,
put/call walls) → esperar **volumen probando** el nivel → entrar. **Paciencia**: no operar cada 5 min.

---

# SERIE $25K CHALLENGE Pt. 1-4 (trading en vivo) — solo lo NUEVO

> Episodios de trading en vivo del reto. **Refuerzan el método**; poco net-new. Lo que sí suma:

## Manejo de LEAPs (de la discusión de IREN — te aplica directo)

> Nota: en el transcript "iron" = **IREN** (la acción que tú tienes; Whisper la oyó mal).

- ⭐ **"Un LEAP es un hold de largo plazo que swingueas en el camino":** mantienes la posición y
  **vendes ALGUNOS contratos en cada subida** (ej. compraste a 30, vendes parte a 42, o aguantas y
  vendes a 45). = exactamente lo que hablamos de tu MSFT.
- ⭐ **Delta como PROBABILIDAD:** delta .30 = **~30% de probabilidad** de terminar ITM (70% de no).
  Úsalo para dimensionar el riesgo del strike.
- ⭐ **Theta mata los LEAPs muy OTM sin valor intrínseco:** un call lejano (ej. IREN 110 con la
  acción en 42) es "puro tiempo que pagas" → **rueda (roll) el contrato antes de que theta lo
  borre**, cuando el subyacente se acerque. No compres demasiado OTM para el mes cercano; compra
  **ITM o cercano** (mira el delta). Ver [[option-chain-statistics-tabla]].

## Detalle del filtro de flujo (para replicarlo)

single-leg · **filtrar OUT multi-leg** · **Intermarket Sweep Order (ISO)** = orden institucional
que barre varias bolsas (urgencia) · **premium > $100k** · descendente → **guardar como filtro
propio**. (Los multi-leg pueden ser butterflies/calendars/diagonales → confusos; por eso single-leg.)

## ⚠️ Nota honesta para TI (importante)

El método que enseñan es **DIRECCIONAL** (comprar calls/puts según flujo + GEX) — distinto de tu
core de **iron butterflies 0DTE / vender prima**. Lo que MÁS te sirve de MarketSnack es **el lado
GEX**: régimen **gamma+ = pin/range = bueno para mariposa**; **gamma− = volátil = malo para
mariposa** (mejor esperar el crush). El lado de **flujo/contract-details** te sirve más para tus
**LEAPs direccionales** (MSFT, IREN, PLTR) y para leer techos/pisos. Ver
[[sistemas-separados-0dte-vs-confluencia]], [[no-vender-prima-en-semana-earnings]].
