# 🔍 Retrospectiva — 2026-07-29 (día FOMC) · SPX 0DTE

> Objetivo: convertir el día en data. Qué pasó, qué NO hicimos bien, qué trades SÍ
> se dieron, y un **playbook para entrar/salir rápido**. Research/educación — Tania
> decide y ejecuta; esto no es asesoría de inversión ni una orden.

## 1. Los números del día (fuente: FMP ^GSPC/^VIX; VS3D/GEX/straddle de Tania)
- **SPX:** apertura 7,418 · **máx 7,450.84** · **mín 7,319.43** · **cierre 7,320.24 (−1.46%)**.
- **VIX:** apertura 18.27 · **mín 17.45** · **máx 20.44** · **cierre 20.42 (+12%)**.
- **Straddle 0DTE:** ~57–58 pre-Fed → **crush a ~36** (2:14 PM) → **re-expandió** al cierre.
- **GEX (MarketSnack):** Net GEX −12.9B (AM) → −3.1B (post-Fed, sanó) → re-expandió.
  - **Gamma Flip:** ~7,415–7,430 (día) → **7,401** (cierre).
  - **Magnet (etiqueta):** 7,500 (apertura) → 7,300 (~10:15) → **7,450** (post-Fed) — pin pasajero.
  - **Put Wall (imán durable):** 7,300 → 7,390 → **7,380 (3.4B)** — la mayor gamma del día.
  - **Call Wall:** 7,440–7,475.

## 2. La película (timeline)
| Hora ET | SPX | VIX | Evento |
|---|---|---|---|
| 9:00 (pre) | ~7,420 | 18.3 | 0DTE, straddle 57.40, gamma negativa |
| 10:00–10:15 | 7,399→7,374 | 19.2→19.4 | selloff, rompió 7,420 y 7,390; MVC cae 7,500→7,300 |
| 12:05–12:15 | **7,346 (mín 7,341)** | **20.34** | test del **muro 7,350**; VIX cruza 20; VETA total |
| 1:12–1:32 | 7,378→7,390 | 19.2 | rebote, retando el flip |
| 2:00 | 7,384 | 19.4 | **FOMC** (comunicado) |
| 2:14 | 7,410 | **17.45** | **CRUSH** (VIX 20.34→17.45, straddle 55→36) |
| 2:53–3:05 | **7,450 (máx)** | 17.5 | cruzó flip, **PIN fugaz 7,440–7,450** |
| 3:14 | 7,419 | 18.2 | **PIN FALLÓ** — rompió el flip a la baja |
| 3:31 | 7,380 | 19.0 | reversión al **Put Wall** |
| 3:48–4:00 | 7,334→**7,320** | 19.9→**20.42** | rompió 7,380 y 7,350; **cierre en mínimos** |

## 3. El diagnóstico clave: fue un DÍA DIRECCIONAL (bajista), NO de pin
- **Gamma negativa casi todo el día + VIX subiendo** = régimen de **amplificación** → el mercado
  quería **MOVERSE**, no pinear. La compresión (crush) fue **fugaz** (round-trip 20.3→17.4→20.4).
- El **imán durable (Put Wall 7,300–7,380)** estuvo abajo TODO el día. El precio gravitó hacia él.
- **La mariposa (venta de prima) fue la herramienta EQUIVOCADA hoy.** Correcto NO operarla — pero
  el edge estaba en ir **DIRECCIONAL con la caída**, no en vender prima.

## 4. Los trades que SÍ se hubieran dado (en retrospectiva)
> Ambos fueron **BAJISTAS/direccionales**, a favor de la gamma negativa, hacia el Put Wall.

**A) Short de la mañana — 7,420 → 7,350 (~70–80 pts)**
- **Gatillo:** gamma negativa + VIX subiendo + ruptura de 7,410/7,390 con volumen.
- **Objetivo:** el mega-muro 7,350. **Salida:** en 7,350 (imán/piso) o al frenar el momentum.
- Expresión: puts / put debit spread 0DTE (direccional), NO venta de prima.

**B) El TRADE del día — reversión short 7,450 → 7,320 (~130 pts) 🎯**
- **Gatillo LIMPIO:** el **pin de 7,450 falló = ruptura del gamma flip 7,429 a la baja (~3:14 PM)**.
  Eso confirmó que el imán durable (Put Wall) reasumía el mando.
- **Objetivo:** Put Wall 7,380 → 7,300. (Rompió 7,380 y siguió a 7,320.)
- **Salida:** en el Put Wall 7,380, o trailing hasta el cierre.
- Este es el **modelo de "trade rápido": trigger claro → objetivo claro → ~130 pts en ~1h.**

**C) Lo que NO era trade:** la iron butterfly. El pin falló y el crush revirtió → habría sido trap.

## 5. Qué NO hicimos bien (autocrítica honesta)
1. **Visión de túnel con la mariposa.** Pasamos el día preguntando "¿cuándo hacemos el fly?"
   cuando el mercado gritaba DIRECCIONAL. Vimos las dos grandes caídas como espectadores
   ("niveles para el fly"), no como setups bajistas operables.
2. **Nos anclamos en la etiqueta "Magnet 7,450"** post-Fed en vez de pesar el muro más grande
   (Put Wall). Tania lo corrigió, no nosotros primero.
3. **Tratamos el crush como LA señal** sin ponderar que en día hawkish-fade el crush puede
   revertir (y revirtió).
4. **Schwab caído todo el día** → sin greeks/volumen/GEX propios; la renovación se dejó "para
   la tarde" y no se hizo en sesión. Dependimos 100% de las capturas de Tania para el GEX.
5. **Sin plan de trade rápido pre-armado** → todo fue análisis reactivo, no trigger→entrar→salir.

## 6. PLAYBOOK — pasos para estar listos para un trade RÁPIDO (entrar y salir) ⭐
> Reusable. La meta: que cuando aparezca el gatillo, entres en segundos y salgas con regla.

### Antes de abrir (prep)
- [ ] **Schwab renovado** (precio/cadena/greeks en vivo) → `gex.py` + volumen + deltas live.
- [ ] Marcar catalizador del día (FOMC/CPI/earnings) → **expectativa de régimen**.
- [ ] Anotar los niveles GEX: **Gamma Flip, Put Wall, Call Wall, imán más grande** + Gann/VS3D.
- [ ] Tener **tickets pre-armados** en el broker (put spread, call spread, iron fly) como plantillas.

### El árbol de decisión (régimen → tipo de trade)
- **Gamma NEGATIVA + VIX subiendo** → **DIRECCIONAL** (ve CON el movimiento; short al Put Wall /
  long al Call Wall). ❌ NO vender prima.
- **Gamma POSITIVA + VIX calmo/crusheado** → **VENTA DE PRIMA** (iron butterfly en el imán durable).
- **Ruptura del Gamma Flip** = cambio de régimen: **cruza arriba = alcista/pin · rompe abajo = bajista/direccional.**

### Gatillos de ENTRADA rápida (pre-definidos)
- **Direccional:** ruptura de nivel clave (ej. Put Wall/soporte) **con volumen + VIX a favor** →
  entra la pata direccional hacia el siguiente muro.
- **Reversión (el trade de hoy):** **ruptura del gamma flip** en contra del pin → entra hacia el
  imán durable.
- **Pin/fly:** precio **EN** el imán durable + gamma positiva + VIX crusheado → iron fly ahí.

### Reglas de SALIDA rápida (pre-definidas)
- **Direccional:** objetivo = siguiente muro/imán → sal ahí, o si el momentum frena / VIX revierte.
  **Stop:** vuelta a través de tu nivel de entrada.
- **Fly 0DTE:** sal si el precio abandona la zona de ganancia o si el flip se voltea en contra.
- **Stop de tiempo:** en 0DTE, define "no más tarde de las X" (evita quedar atrapada al cierre).
- **Regla de Tania:** en venta de prima, **crédito > pérdida máxima** o no es entrada.

### Herramientas para que sea RÁPIDO
- Schwab live (no dejarlo vencer — renovar semanal).
- `gex.py` calculando Magnet/walls/flip en vivo (independiente, calibrado).
- `mapa_en_vivo` (confluencia 3 lentes + volumen) dando go/no-go.
- Tickets pre-armados + alertas por email en niveles clave (no mirar la pantalla todo el día).

## 7. Próximos pasos concretos (para construir)
1. **Renovar Schwab** (recurrente; no dejar que se caiga).
2. **Calibrar `gex.py`** vs el MVC de compañeros (QuantData) / GEX de MarketSnack → imán propio.
3. **Codificar el árbol de régimen** en la salida de `confluencia.py`: que auto-clasifique
   **día direccional vs día de pin** (gamma +/− y dirección del VIX).
4. **Pre-armar tickets** de las 3 estructuras en el broker.
5. **Definir por escrito** las reglas de entrada/salida por régimen (este playbook) y practicarlas.

## Lecciones (ya en Memoria)
imán durable > pin pasajero · crush día-FED puede revertir · gatillo del giro = ruptura del
flip · ventana fly 0DTE día-FED corta (~2:15–2:45) · "más prima" con vol subiendo = riesgo.
