# ⚙️ Gamma, Charm y lectura de Market Makers en 0DTE — resumen

**Objetivo:** no analizamos **dirección**, analizamos **comportamiento** — cómo se
comporta el mercado bajo las condiciones de liquidez de hoy. Tres herramientas:
**Gamma, Charm, Straddle.**

## Delta → Gamma → Charm
- **Delta** = cuánto cambia el valor de la opción cuando se mueve el SPX.
- **Gamma** = cuánto cambia el **delta** cuando se mueve el **precio**.
- **Charm** = cuánto cambia el **delta** con el **paso del tiempo**.
Los MM se mantienen delta-neutral → ajustan comprando/vendiendo futuros.

## Gamma NO predice dirección — describe comportamiento
Un Gamma Profile NO es verde=compra / rojo=venta. Es:
- **verde = más provisión de liquidez** · **rojo = menos liquidez / posible amplificación.**

| Régimen | Qué hacen los MM | Efecto |
|---|---|---|
| **Gamma positiva** | operan CONTRA el movimiento (venden en subidas, compran en caídas) | **CONTIENE** — más liquidez, menos vol, vuelve al balance |
| **Gamma neutral** | menos cobertura | **DEJA MOVER** — sensible a noticias/flujos |
| **Gamma negativa** | operan CON el movimiento (compran arriba, venden abajo) | **ACELERA** — menos liquidez, más vol |

> **Gamma positiva contiene · Gamma neutral deja mover · Gamma negativa acelera.**
> El mercado no necesita estar en gamma negativa para cambiar de carácter: basta con que se vuelva neutral.

## Métricas institucionales
- **Dollar Per Percent:** cuánto cambia el delta de los MM si el SPX se mueve 1%
  (ej. $10-12B normal). No dice dirección, dice **sensibilidad del sistema.**
- **Dollar Value of Trade:** tamaño en $ del hedge que tendrían que hacer. Positivo→compra, negativo→venta.

## Charm (el reloj)
- En 0DTE el tiempo se consume rápido → aunque el SPX no se mueva, el delta cambia
  y obliga a re-cubrirse. Puede generar presión compradora/vendedora, sobre todo
  hacia la **segunda mitad de la sesión (~1 PM).**
- **Gamma puede contener el movimiento; Charm puede inclinarlo.**

## Combinar Gamma + Charm
- Gamma+ y Charm ayuda → estable. · Gamma+ pero Charm vendedor → contenido pero pesado.
- Gamma neutral y Charm vendedor → más fácil caer. · Gamma− y Charm en la misma dirección → riesgo de aceleración.

## El Straddle y Spot vs Straddle
- **Straddle** = cuánto movimiento paga el mercado (call+put ATM). No es predicción.
- **Lección clave:** el **Spot puede moverse fuerte y el Straddle caer al mismo
  tiempo** — el tiempo destruye extrínseco más rápido de lo que el movimiento lo crea.
- > **En 0DTE, dirección no es suficiente. El movimiento tiene que ganarle al tiempo.**

**Guía Spot vs Straddle:** Spot↓ Straddle↑ = pagan por riesgo · Spot lateral
Straddle↓ = castigan al comprador (premian al vendedor de prima) · Spot↑ Straddle↓
= subida con compresión de vol.
