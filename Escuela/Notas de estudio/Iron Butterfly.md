# 🦋 Iron Butterfly — resumen para repaso

**Qué es:** estrategia de **crédito con riesgo definido**. Vendes el centro (tipo
straddle) y compras alas para limitar la pérdida. "Short straddle con airbags."
Ganas si el precio **muere cerca del centro** al vencimiento.

**Se beneficia de:** paso del tiempo (Theta +) y contracción de IV (Vega −).
**Se usa cuando:** esperas mercado **lateral / en rango**.

## Estructura (4 patas)
1. Vender Call (centro) · 2. Vender Put (centro) · 3. Comprar Call OTM (ala) · 4. Comprar Put OTM (ala).

## Números clave
- **Max Profit** = crédito recibido.
- **Max Loss** = ancho del ala − crédito.
- **Break-evens** = centro ± crédito.
- Ejemplo: centro 100, alas 95/105, crédito 2 → max profit 2, max loss 3, BE 98 y 102.

> ⚠️ **Tu regla:** crédito > pérdida máxima (crédito > 50% del ancho). Eso aprieta
> la mariposa y sacrifica probabilidad (< 50%) a cambio de mejor ratio. Es tu
> estilo — la de libro deja max loss > max profit.

## Las griegas
- **Theta (+):** quieres que pase el tiempo.
- **Vega (−):** te favorece que baje la IV.
- **Gamma (−):** cerca del vencimiento el riesgo se dispara si se mueve → **0DTE es peligroso** (lo controlas con tu lectura de gamma/dealer).
- **Delta (~0):** neutral al inicio; se inclina si el precio se desplaza.

## Cuándo SÍ / cuándo NO
- **SÍ:** rango, IV alta con posible contracción, sin eventos, buena liquidez.
- **NO:** antes de earnings/macro (gaps), tendencia fuerte, spreads amplios, si no estarás atento.

## Selección
- **Centro:** donde el mercado gravita (tu **imán** / zona de equilibrio).
- **Alas:** fuera del movimiento típico (fuera del straddle del día).

## Gestión (lo más importante)
- **Take profit: 50–70% del crédito.** El último tramo tiene mal ratio.
- **Zonas:** 🟢 cerca del centro · 🟡 cerca del BE (vigilar) · 🔴 cerca del ala (decidir ya).
- **Stop:** pierdes 1–1.5× el crédito, o rompe BE y no vuelve, o delta muy direccional.
- **Ajustes:** cerrar temprano (el mejor para gestionar), rolar el centro, o convertir a cóndor.

## Riesgos reales
Asignación temprana (ITM cerca de vencimiento) · pin risk · gaps · liquidez.

## La lección de cierre
> **La clave no es el setup, es la gestión: TP temprano + reglas de salida.**
> Evita eventos y 0DTE al inicio (el gamma castiga). Menos operaciones, más selectivas.
