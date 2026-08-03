# 📈 La Curva del SPX — resumen para repaso

**Idea madre:** la cadena de opciones es un **mapa de probabilidades**, no una
lista de productos. Dibujas esas probabilidades y sale una **campana**.

## Cómo leer la campana (3 cosas)
- **Pico** = dónde el mercado cree más probable que acabe el SPX.
- **Anchura** = cuánto espera moverse (= el straddle).
- **Inclinación (skew)** = hacia dónde tiene miedo.
- **Regla de oro:** la altura de la curva sobre un precio = probabilidad de acabar ahí.

## El secreto
Cada precio ya es una probabilidad, escondida en las opciones. Una mariposa que
cuesta 15¢ por dólar → el mercado le da **15% de probabilidad** (la que *cobra*,
no necesariamente la que ocurre).

## Por qué la curva se inclina a la izquierda (skew)
1. Las bolsas **caen por el ascensor** (caídas grandes más probables) — honesto.
2. Todos compran **el mismo paraguas** (puts) → seguro caro, no pronóstico.
3. El cerebro **exagera el miedo** → pagamos de más por protección.

## Los 3 niveles del dealer (los que mandan)
- **Call Wall** = techo. El dealer vende ahí y frena la subida (resistencia).
- **Put Wall** = suelo. El dealer compra ahí y sostiene (soporte).
- **Gamma Flip** = línea de calma.
  - **Encima:** mercado TRANQUILO — el dealer amortigua, el precio se pega al pico.
  - **Debajo:** mercado NERVIOSO — amplifica; cada caída empuja más ventas (el ascensor).

## Natenberg — 4 volatilidades
Pasado (hecho) · Futuro (lo único que importa, nadie lo sabe) · Tu apuesta (tu
campana) · Lo que cobra el mercado (ya en el precio).
**Tu ganancia = lo que cobra el mercado − lo que de verdad pasa. La dirección casi no importa.**

## Cada estrategia apunta a una zona
- **Bull Put Spread** → cola izquierda (vendes miedo cobrado de más).
- **Iron Butterfly** → el pico (mercado tranquilo, sobre el Gamma Flip).
- **Iron Condor** → el cuerpo (ni techo ni suelo llegan).
- **Bear Call broken-wing** → la inclinación (miedo exagerado).

## La frase para tatuarse
> **No operas el precio. Operas la diferencia entre tu campana y la del mercado.**
> No adivines dónde acaba el SPX — encuentra dónde el miedo está mal cobrado.
