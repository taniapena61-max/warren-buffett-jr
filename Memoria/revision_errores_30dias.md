# Revisión de errores 30 días (23-ago → 22-sep-2026)

> Pedido por Tania 2026-09-22: "los errores que me han hecho perder por hacer lo que me
> dices". Fuente: `Memoria/errores.md` + trades cerrados (`API/posiciones.json`) + registro
> Tito. SIN adivinar. Claude relee este archivo al arrancar para NO repetir.

## 0) La foto real del dinero (trades CERRADOS, según los registros)
- **Ganados:** SPX fly 7630 +$105 · SPX fly 7675 +$80 · ORCL fly +$98 · MULL put 20.6 +$127 ·
  MULL put 23 +$120  →  **+$530**
- **Perdidos:** SPX fly 7525 −$125 · HIMS fly 30 −$18 · **SPX fly 7750 (hoy) −$185**  →  **−$328**
- **Neto realizado ≈ +$197** en 30 días (los flies 0DTE dan neto positivo chico).
- ⚠️ **Lo que NO cuadra con "pierdo a diario":** el daño real NO está en los flies cerrados
  (netos +$197). Está en (a) las ENTRADAS QUE PERDÍ por dudar, y (b) posibles pérdidas
  grandes en papel de las LEAPs abiertas (HIMS 40C −92%, META 1430C) — **sin tesis en archivo,
  necesito que me confirmes si esas 2 fueron recomendación mía o tuya** antes de contarlas.

## 1) PATRÓN #1 — Destino equivocado (foto vs simulación) ⭐⭐⭐ el que más cuesta
- **22-sep SPX fly 7750:** ancle en el $Value 7750 (foto) e ignoré el cono/VWAP que decían
  7775 (arriba). Precio se fue a 7775. **−$185.** [[simulacion-cono-manda-sobre-value-foto]]
- **11-sep SPX cierre:** cuerpo 7675 (closeTarget Tito) vs pin real 7667 → mis-centrado.
  Gané +$80 pero Nancy centró en el pin real 7665 y sacó **+$396** el mismo día.
- **FIX (dura):** el destino lo da la SIMULACIÓN (cono maestra + charm) + dónde el precio
  REALMENTE pinea (tape/rangeClose), NO el imán estático ni el closeTarget alto. Si cono y
  $Value discrepan → manda el cono. VWAP arriba del precio = jala arriba. **Si dividido, doy
  las DOS entradas y eliges tú.**

## 2) PATRÓN #2 — P&L de modelo en vez de mark del broker
- **11-sep ORCL:** canté el P&L 2 veces mal antes del fill real. **16-sep FOMC:** dije
  "pérdida máxima" sin restar el extrínseco (era +$265, no pérdida).
- **FIX:** NUNCA cantar P&L sin el mark del broker. Con DTE>0, "spot pasó el ala" ≠ pérdida
  máxima. [[nunca-pl-de-modelo-usar-mark-broker]]

## 3) PATRÓN #3 — Describir/dudar en vez de ENTREGAR → pierdo la ventana
- **3-sep:** te dije "espera el pin asentado (tarde)" → para las 2pm ya no había prima.
- **16-sep FOMC:** pin+crush confirmados y me quedé "debatiendo el régimen" → la fly
  simulada dio **+$462 (+63%)** que no entregué.
- **FIX:** pin + straddle crushando en los últimos 15-30 min = **dar la fly YA** (con GATE),
  no describirla. El régimen es nota de riesgo, no veto. [[metodo-cierre-dar-la-fly-no-solo-describirla]]

## 4) PATRÓN #4 — Reglas rígidas que vetan trades +EV
- **11-sep:** salté un fly de cierre por ratio 0.8:1 → habría sido **+$205** (el pin aguantó).
- **1-sep DELL:** veté un setup de earnings de manual ("un loto") por miedo macro → abrió **+10%**.
- **FIX:** al wire, calcular **EV (P_dentro × premio vs P_fuera × pérdida)**, no vetar por el
  ratio literal. Earnings = sistema separado del régimen del índice. [[gate-demasiado-rigido-nunca-entra]]

## 5) PATRÓN #5 — Cuerpo del fly ATM / no "lejos"
- **2-sep AMZN:** propuse el cuerpo EXACTAMENTE en el precio (apuesta a que no se mueve) con
  los lentes diciendo lo contrario. (Lo cazaste tú, sin pérdida.)
- **22-sep (hoy):** te dije "entra al TOQUE del 7755" = ATM = prima muerta. Corregido.
- **FIX:** cuerpo en el destino, entrada LEJOS (precio a 15-20pt del cuerpo = prima gorda),
  nunca al toque del cuerpo. [[call-la-entrada-lejos-en-tiempo-real]]

## Compromiso operativo (lo que hago distinto desde mañana)
1. **Destino por simulación+VWAP**, y cuando esté dividido te doy ARRIBA y ABAJO.
2. **Entrego el strike con gatillo**, no describo — pin+crush = fly YA.
3. **EV, no ratio literal**, en el cierre.
4. **Mark del broker** para todo P&L.
5. Releo ESTE archivo + `errores.md` al arrancar cada día.

---

# AUDITORÍA: Ponencia Roos (VS3D) → código (22-sep, verificado línea por línea)

## ✅ CABLEADO en el núcleo (verificado)
1. Régimen γ+/γ− primero — `odte` / `selector_metodo`.
2. Flip "vender→comprar" (rebote mecánico del MM) — `flip_level.py`.
3. Stat "3 cierres γ≤0 → rango ~6%" — `gamma_expansion.py` (tarea 16:10).
4. Imán que migra = no fly — `pin_estable.py`.
5. Charm = destino del settle (tarde) — `watch_cierre_charm.py`.
6. **SIMULACIÓN > foto (cono manda sobre $Value/pin)** — `flip_level.py` + `selector_metodo.py` (HOY).
7. Vanna intradía (mañana = ruido/picos vol → no fly temprano) — `zerodte.py`.

## 🟡 PARCIAL (se usa pero no operacionalizado)
8. Charm "sesgo casi siempre ARRIBA" — se usa charm en el cierre, pero el sesgo direccional
   al alza NO está codificado como inclinación del destino.
9. "Flujo (MS) = contexto, NO señal de hedging" — solo mención en `checklist_entradas`, no un
   guard duro en el código que impida usar MS-flow como señal.

## 🔴 FALTA (ni código ni alerta — los huecos reales)
10. **Vanna macro de Roos:** "vol baja + evento (Fed) enfrente → el MM VENDE futuros" +
    "VIX salta y se desvanece → rebota casi donde empezó". No hay alerta pre-Fed ni de VIX-fade.
11. **Trampolín / recompra forzada al expirar:** "cuanto más vende el MM, más compra obligatoria
    hay cuando la posición expira = rebote". No codificado (el flip lo roza, pero no el timing).
12. **ETFs apalancados 2x/3x amplifican el CIERRE** (rebalanceo EOD misma dirección): no fadear
    la última hora en día trending; TSLL/MULL decaen. Solo en memoria, no un flag de la ventana de cierre.

**Plan:** 6 ya está (hoy). Faltan 8-9 (operacionalizar) y 10-11-12 (construir). Prioridad a definir con Tania.

## ACTUALIZACIÓN 22-sep (tarde) — construidos #10 y #12
- ✅ **#12 EOD amplify guard** (`scripts/eod_amplify_guard.py`) — en día tendencial + ventana de
  cierre avisa "NO fadear el cierre, ETF 2x/3x amplifican el EOD". Cableado en `estado_sistema §12`.
- ✅ **#10 Vanna guard** (`scripts/vanna_guard.py`) — (A) VIX-fade = rebote (detecta spike→fade con
  su propio log `historial/vix_intradia.jsonl`), (B) pre-evento = venta mecánica (lee
  `historial/eventos_macro.json`). Cableado en `estado_sistema §11`.
- **FALTA que Tania/Claude registre la próxima fecha FOMC/CPI VERIFICADA** en `eventos_macro.json`
  para activar la parte (B) — no se adivina.
- **Quedan pendientes:** #8 (charm sesgo arriba operacionalizado), #9 (guard duro MS-flow=contexto),
  #11 (trampolín/recompra forzada al expirar).

## CIERRE 22-sep — clase Roos 100% integrada (12/12)
- ✅ **#8** charm sesgo-arriba — regla en `selector_metodo` (aparece en ventana de cierre 0-150min):
  "si el settle esta indeciso entre 2 destinos, inclina al de ARRIBA".
- ✅ **#9** MS-flow = contexto — guard/recordatorio en `selector_metodo` (siempre): "flujo != posicion,
  el nucleo es $Value/VS3D". Verificado que MS-flow NO alimenta ningun score direccional (no era bug).
- ✅ **#11** trampolin — `scripts/trampolin_guard.py` (cableado `estado_sistema §13`): cerca de OPEX/quad-
  witch + MM vendiendo (γ−/bajo flip) + put wall -> avisa "rebote post-vencimiento por recompra forzada".
- **TODA la ponencia Roos esta ahora en codigo/nucleo (12 puntos).** Pendiente unico: registrar la
  fecha VERIFICADA del proximo FOMC en `historial/eventos_macro.json` para activar vanna-(B).
