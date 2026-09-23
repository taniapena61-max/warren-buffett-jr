# Clase MarketSnack/InfusionTV — 2026-09-16 (flujo como dirección, día FOMC)

> Fuente: transcripción en `Escuela/Materiales/Clase MarketSnack 2026-09-16 (FOMC, flujo direccional) - transcripcion.txt`.
> Estudiada 22-sep. Regla de Tania: si hay algo NUEVO se aplica; si no, se guarda.

## NUEVO (accionable)
1. **Filtro de régimen por FLUJO (el core de esta clase):** durante ~1 mes NO hubo compra de
   calls agresiva — solo put buying + VIX calls (bajista). Regla: **mientras no veas call buying
   institucional + venta de puts, NO compres calls / sesgo bajista.** El giro alcista se confirma
   cuando el flujo muestra calls entrando + puts vendiéndose. "Late shorters get wrecked" (no
   perseguir el short tarde; short en resistencia con plan, o esperar volumen).
2. **Tell pre-catalizador:** puts ATM/OTM comprándose a IV BAJA y delta BAJA ANTES de una noticia
   = smart money posicionando la dirección. (747 put 9:43am pre-FOMC → +mucho a las 3pm.)
3. **Venta de premium en calls = tell bajista de ese nombre** (ej. TSLA vendiendo el 360 call
   oct-2 = esperan TSLA<360 = short). Puts institucionales persistentes y en ganancia = el "clue"
   para short (BX, SMH, XOM).

## YA LO TENÍAMOS (solo guardar)
- Septiembre estacionalidad horrenda · quad-witch viernes (rebalanceo/volumen) · γ negativa +
  magnet 7500 · niveles de tape (7580 soporte, 7509, 7450) · día FED (hawkish, drop). Ver
  [[metodo-gex-victor-infusiontv]], [[seasonality-midterm-2026]], [[dia-fed-esperar-revalorizacion]].

## ✅ CONFLICTO RESUELTO (Tania eligió SÍNTESIS, 22-sep) — YA APLICADO
- Decisión: **flujo = sesgo de CONVICCIÓN institucional → CONFIRMA, no lidera; NO es hedging
  (Roos) NI el núcleo ($Value/VS3D).** El núcleo manda; el flujo confirma.
- Aplicado: `scripts/flujo_regimen.py` (calls vs puts, filtra LEAPs) escribe
  `historial/flujo_regimen.json`; `selector_metodo.py` lo lee y lo muestra como "[Flujo #9]
  REGIMEN … = convicción que confirma". Guard #9 reformulado a la síntesis. Ver
  [[flujo-conviccion-confirma-no-lidera-sintesis-roos-ms]].

## (histórico) El conflicto original — Roos vs MS
- **Roos (ayer):** "los escáneres de FLUJO son peligrosos, flujo ≠ posición, no hay edge; el
  $Value/OCVS es la verdad." → ayer cablé #9: "flow = contexto, NO señal direccional".
- **Esta clase MS:** "el FLUJO ES la dirección — el put buying te avisó la caída."
- **Reconciliación PROPUESTA (a confirmar con Tania):** ambos coinciden en que flujo ≠ hedging
  y que el NÚCLEO es el $Value/VS3D. Difieren en si el flujo PREDICE dirección. Síntesis:
  **flujo = sesgo de CONVICCIÓN institucional (útil como confirmación/contexto), NO señal de
  hedging (Roos) NI el núcleo — confirma, no lidera.** Si Tania acepta, ajustar el guard #9 a
  esa redacción y añadir un "régimen de flujo (calls vs puts)" como capa de contexto en selector.
- Ver [[vs3d-ocvs-firmado-exchange-flujo-no-es-hedging]], [[aplicar-clases-ms-flow-siempre]].
