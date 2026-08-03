# VS3D — Curva semanal de probabilidad (material de clase)

> Material de la clase **Membresía Élite Swing Trading (VS3D)**, compartido por
> Tania el 2026-07-24. Es la base teórica del análisis de SPX que hacemos.

## Concepto (texto de la clase)

**Evolución de la curva semanal (Lunes → Martes → Miércoles → Jueves).**

Esta evolución permite construir un **mapa probabilístico de la semana**. La
combinación de:
1. la **compresión del straddle**,
2. la **redistribución diaria de la probabilidad**, y
3. la **actualización de los deltas estructurales**

deja **rangos semanales claramente definidos**, que sirven como referencia para
interpretar el comportamiento del mercado e identificar zonas con mayor
probabilidad de reacción. En lugar de basar el análisis únicamente en el precio,
estas curvas incorporan el **componente probabilístico** y muestran cómo cambian
las expectativas del mercado a medida que se acerca el vencimiento.

El gráfico son **campanas de densidad de probabilidad (PDF)** superpuestas, una
por día, que se **estrechan y recentran** de lunes a jueves conforme cae el
tiempo hasta el vencimiento. Eje X = Delta / Precio SPX; eje Y = densidad de
probabilidad.

## Los 4 mecanismos (detalle de la clase, 2ª parte)

1. **Compresión progresiva de la distribución.** Curvas amarilla (lunes), cian
   (martes) y magenta (miércoles) muestran compresión continua: cada día la curva
   se vuelve **más alta y más estrecha** — menos tiempo para movimientos amplios
   antes del vencimiento.
2. **Reducción del straddle.** Ejemplo de la clase: el straddle pasó de **~67.9
   pts (cierre martes) a ~56.9 pts (miércoles)** — evidencia del time decay y del
   rango implícito que se reduce para el resto de la semana.
3. **Mayor concentración de probabilidades.** El miércoles el pico es mucho más
   pronunciado alrededor del precio actual: el mercado concentra más probabilidad
   en un rango estrecho. Al acercarse el vencimiento, la distribución **pierde
   amplitud y gana definición**.
4. **Actualización de los deltas estructurales.** Los puntos de puts (rojos) y
   calls (verdes) con deltas **0.10, 0.15 y 0.25** se desplazan y quedan más
   próximos al precio, reajustándose según el movimiento del SPX, la IV y el paso
   del tiempo.

> **Ojo (para el reporte de apertura):** la clase marca deltas **0.10 / 0.15 /
> 0.25**. Tania pidió el reporte con **0.20 / 0.25 / 0.30**. Confirmar si quiere
> alinear el reporte con la clase (agregar 0.10 y 0.15) o mantener su set.

## Cómo se traduce a datos verificables (Schwab)

Cada campana es una **distribución lognormal** del precio:
- **Centro** = precio spot (Schwab en vivo).
- **Ancho (σ)** = del **straddle ATM** (call ATM + put ATM) de ese vencimiento.
  `movimiento_esperado ≈ straddle` ; `±1σ ≈ spot ± straddle` (68%);
  `±2σ ≈ spot ± 2·straddle` (95%).
- **Compresión** = el straddle baja día a día (theta) → la campana se angosta.
  Verificado el 2026-07-24: $38.90 (pre) → $32.50 → $30.50 → $12.95 (tarde).

Piezas ya construidas que alimentan esto:
- **Straddle por vencimiento**: `scripts/deltas_apertura_spx.py` (misma cadena Schwab).
- **Deltas estructurales .20/.25/.30**: mismo script, reporte de apertura 9:32 AM.
- **Diario de SPX**: `historial/spx_diario/` — ver [[diario-spx-mercado]].

## 5. Implicación para el trading (cierre de la clase)

Al cierre del miércoles, la curva semanal presenta rangos probabilísticos **mucho
mejor definidos** que al inicio de la semana. La combinación de distribución más
concentrada + straddle más reducido + deltas estructurales actualizados da un
**marco estadístico más preciso** para interpretar el mercado, identificar zonas
de mayor probabilidad y planificar operaciones con más confianza en las sesiones
restantes hasta el vencimiento.

**Observación clave:** el **centro** de la distribución permanece muy cercano a
la zona de **~7,500** mientras el precio se desarrolla alrededor de ese nivel.
Es decir: pese a los movimientos intradía, el mercado **mantiene una expectativa
estable del cierre semanal más probable**, pero con un **rango cada vez más
estrecho** por la aceleración del time decay. Esta es justo la evolución esperada
en una semana **sin expansión significativa de la volatilidad implícita**.

> Lectura operativa: centro estable + rango que se angosta = el imán semanal no
> se mueve, pero la certeza sobre él crece día a día. Encaja con la estrategia de
> Tania de posicionarse EN el imán (ver [[estrategia-contraria-posicionarse-en-el-destino]]).

## Pendiente (acordado 2026-07-24)
- Construir la **curva semanal probabilística** con Schwab: campanas ±1σ/±2σ por
  vencimiento lun→vie, mostrando la compresión, replicando el gráfico de la clase
  con números auditables.
- **Verificar VS3D vs Schwab** al mismo minuto (Tania perdió acceso el viernes;
  se hace el lunes en la apertura).

Confluencia completa de Tania: **VS3D + MarketSnack + Square of Nine** — ver
[[marketsnack-plataforma]] y [[square-of-nine-calculadora]].
