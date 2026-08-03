# 🌡️ El VIX — resumen para repaso

**Idea madre:** el VIX **no mide el miedo, mide cuánto cuesta hoy asegurar al
S&P 500.** Es una **factura, no un pronóstico.** Y ese precio depende menos de lo
que vaya a pasar que de **cuánta gente quiere el mismo seguro a la vez.**

## Qué es de verdad
- El VIX = **la anchura de tu campana, con precio** (desviación estándar del SPX
  a 30 días, anualizada). No es la IV de una opción — es el **precio de una cesta
  entera** de puts y calls OTM del SPX, ponderados por 1/K.
- Los puts OTM están caros por el skew → parte del VIX **no es movimiento
  esperado, es el precio de la cola izquierda (el miedo).**
- Se muestra como raíz cuadrada de la varianza (VIX 20 → varianza 400).

## La prima de varianza (por qué vender vol paga)
- El VIX **casi siempre miente**: supera a la volatilidad que el SPX realiza
  después en ~3-4 puntos. Esa brecha = **prima de riesgo de varianza.**
- Cuando vendes prima del SPX **no apuestas a dirección: cobras esa prima. Tú eres la aseguradora.**
- Rentable "de media" = muchos meses pequeños en verde y, de vez en cuando, un
  día que devuelve varios. La prima existe porque alguien tiene que aguantar ese día.

## La estructura temporal (la curva)
- **Contango** (lo normal, 80% del tiempo): meses lejanos valen más → erosiona al
  largo de vol, **viento a favor del vendedor de prima.**
- **Backwardation** (curva invertida): la firma del estrés. El régimen cambió →
  recoge velas o ponte largo de convexidad.

## Reflexividad: el VIX no observa la caída, la EMPUJA
- Sube más rápido en las caídas de lo que baja en las subidas (correlación ~−0.8).
- Fondos vol-control venden acciones cuando la vol sube → eso baja más el SPX →
  sube más el VIX → venden más. **Bucle que se alimenta solo** (feb-2018, mar-2020).

## Lo que el VIX NO dice
- **VIX bajo ≠ calma:** significa que **nadie se está cubriendo** (complacencia =
  terreno de los desplomes).
- Es el activo grande **más reversor a la media** que existe: los picos no duran.
  Vende miedo cuando todos lo quieren, recómpralo cuando nadie lo mira.

## Cómo se usa (4 lecturas)
1. **Nivel:** <15 complaciente · 15-20 normal · 20-30 elevado · 30+ estrés.
2. **Reversión:** picos > 30-40 no duran → fade el extremo.
3. **Curva:** contango (a favor del vendedor) / backwardation (peligro).
4. **VIX vs realizada:** si el VIX va muy por encima del movimiento real → seguro caro.

## Dos trampas que cuestan dinero
- ❌ "VIX alto = vender opciones": caro no es techo; puede ponerse mucho más caro.
- ❌ "VIX bajo = sin riesgo": la complacencia es donde el shock expande más rápido.

## Para tu operativa
> El VIX **fija la anchura de tu campana.** Antes de elegir strikes por delta o
> colocar tus alas, mira el VIX: te dice dónde caen de verdad tus deltas 25, 16 y 10.
> **La campana, las alas y el VIX son tres vistas del mismo objeto.**
