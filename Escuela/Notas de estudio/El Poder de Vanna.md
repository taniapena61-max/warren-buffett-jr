# 🌀 El Poder de Vanna — resumen (griega de 2º orden)

> **Parte 1 · el motor.** El mapa en pantalla está en
> **[Vanna II (el mapa en VS3D)](El%20Poder%20de%20Vanna%20II%20%28el%20mapa%20en%20VS3D%29.md)**.

**Idea madre:** Gamma dice que el **precio** mueve el delta. Charm, que el
**tiempo** lo mueve. **Vanna** dice algo más sutil: la **volatilidad** mueve el
delta — sin que el precio se mueva ni un punto. Es la griega que explica **los
rallies que suben sin que nadie compre.**

## Las tres puertas (formas de que tu delta cambie solo)
- **Gamma = ∂Δ/∂S** (el precio) · **Charm = ∂Δ/∂t** (el tiempo) · **Vanna = ∂Δ/∂σ** (la vol).
- Doble definición: Vanna = ∂Δ/∂σ = ∂Vega/∂S → **el puente entre el mundo del precio y el de la vol.**

## La intuición
Un put OTM lejano con vol baja tiene delta ~0.05. Sube la vol y ese mismo strike
"parece alcanzable": su delta se hincha a ~0.15. **El precio no se movió, el strike
no cambió — se ensanchó la campana**, y con ella la probabilidad de llegar (= el delta).

## La forma: Vanna es una ONDA, no una rampa
- **Cero cerca del dinero** (donde Gamma es máximo). · **Pico en la zona OTM ~25 delta**
  (la misma marca del skew). · No crece sin fin: tiene máximo y cae a cero.
- ⚠️ Detalle: **Vanna se mueve al revés que la vol.** Es en los **mercados tranquilos
  (vol baja) cuando Vanna es MÁS potente.** La calma no la desactiva: la afina.

## Por qué importa: el inventario del MM
Los MM están **cortos de puts OTM** (el seguro que compran los fondos), justo en
la zona del pico de Vanna (~25 delta). Cuando la vol se mueve, el delta de esa
montaña de puts se mueve y el MM **tiene que cubrirse en futuros. Sí o sí.**

## El motor: el rally que sube sin compradores
1. MM corto puts OTM. 2. La vol baja (vol crush). 3. El delta de esos puts se
encoge. 4. Al MM le sobra cobertura corta → **compra futuros** (sin querer). 5. Esa
compra sube el SPX, el SPX tranquilo baja más el VIX → vuelta al paso 2. **Bucle.**

**El número real:** SPX 7400, MM corto 200,000 puts en 6900, VIX cae de 20 a 17
(sin que el SPX se mueva) → el MM debe **COMPRAR ~$5.0 B** (~13,500 ES). Solo por
3 puntos de VIX y un strike.

## El lado oscuro (el mismo motor al revés)
- **Vol baja = viento de cola** (deriva alcista lenta, terreno del vendedor de prima).
- **Vol sube = acelerador:** el delta de los puts se hincha, el MM vende futuros,
  el SPX cae, la vol sube más. **Vanna + Gamma negativo + fondos vol-control empujan
  juntos hacia abajo** → por eso las bolsas caen por el ascensor.
- **Resaca del OpEx:** al vencer, la montaña de puts desaparece → el viento de cola
  se apaga de un día para otro → semana posterior débil. **Reduce tamaño.**

## Qué mirar en pantalla (la huella de Vanna)
- **VIX moviéndose mientras el SPX no hace nada** = la señal más limpia.
  - VIX↓ SPX plano → **motor alcista cargando** (sesgo alcista aunque el precio no lo muestre).
  - VIX↑ SPX plano → **aviso de venta mecánica** (no vendas puts a la ligera).
- Skew/Risk Reversal 25 (4-6 normal): más skew = más munición de Vanna.
- Percentil VIX: bajo <20 = poco Vanna alcista por exprimir; alto >80 = combustible cargado.
- VVIX >110 = tensión. · Curva contango (a favor alza) / invertida (empuja abajo).

## Operativa
- **Post-evento (Fed/CPI), VIX 2-4 pts abajo:** el mejor terreno del **Bull Put Spread**
  (vendes el suelo con el viento a favor).
- **Semana post-OpEx:** reduce tamaño en ventas de prima.

> **Deja de preguntar "por qué sube" y pregunta "quién tiene que comprar".**
> La mano invisible es una mesa de cobertura. Mira siempre VIX y SPX **juntos.**
