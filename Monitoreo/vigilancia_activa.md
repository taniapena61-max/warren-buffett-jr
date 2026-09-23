# VIGILANCIA ACTIVA — fuente única de verdad de lo que Claude monitorea

> REGLA: Claude LEE este archivo al inicio de cada turno de trading (antes de hablar
> de entradas) y lo ACTUALIZA al armar/desarmar/expirar cualquier monitor. Si un
> método debería estar vigilado y NO está aquí = hueco a tapar. Los monitores de
> sesión EXPIRAN a los 30 min -> re-armar y anotar. Los email-vigilantes son la red
> persistente (corren aunque Claude no esté en sesión).

Última actualización: 2026-09-22 10:12 ET. SPX ~7775, γ+ (netGEX 19.8B, creció), VIX 14.6 → día de PIN fuerte. ✅ **VS3D FRESCO 22-sep propagado a Tito** (fresh:True). Estructura 0DTE: imán/pin dominante **7750** (verde monstruo +4451, = banda baja), resolución gamma-cono ~7776; techo **7780/7783/7785** (rojo) y 7800; piso 7750→7730/7720. Flips (***): rechazo **7783** (VS3D+callWall+Gann), rebote **7755/7740** (VS3D+putWall/flip+Gann). Maestra confirma cono comprimiendo a ~7776. OJO 7760/65 rojos (venden dips). El fly 0DTE 7685/7700/7715 y el GTC Sep18 VENCIERON 21-sep (cerrados). **NUEVO: las 4 flies posicionales SPX (Sep30/Oct16/Oct30/Dec18) quedan bajo la tarea persistente WBJ Monitor Posiciones (cada 10min, email en cada cruce de nivel) — ver sección "SPX 4 FLIES" abajo.**

### Snapshot 2026-09-21 (histórico): γ FLIPEÓ de vuelta a POSITIVO (perfil Gamma VS3D todo verde). SPX gapeó ARRIBA 7650→7697 (+0.62%). Straddle 0DTE $22.35 → banda [7674.7, 7719.4]. Estructura de PIN: imán ~7697–7710 (green VS3D 7700/7705/7710 + Gann Cardinal 7694), techo 7716/7725 (red 7725 + Gann diag 7716), piso 7675 (green VS3D + Gann diag 7672). Reversión SS/Nancy REACTIVADA (pausa del viernes levantada). ✅ VS3D de hoy propagado a Tito (fresh 2026-09-21: sop 7710/05/00/7675/7650, res 7725/7716/7695). Tito OK en 127.0.0.1:3000. ✅ SCHWAB RENOVADO (lunes 21-sep) y Tito ya cargó el token nuevo (broker lens OK, 3362 contratos, delta real). No hace falta reiniciar. Próxima reauth Schwab: ~lunes 28-sep.

## SKILL CLAVE (Tania 18-sep): ANTICIPAR el nivel de REBOTE para entrar
> Calcular ANTES el nivel de rebote (cluster DS2/−2σ + ancla verde VS3D + put wall + Gann) y avisar cuando el precio se ACERQUE, para entrar EN el rebote (toque+giro). Hoy la entrada perfecta fue el dip a 7613/14 (DS2 + ancla 7620). NO perseguir. Ver [[dia-de-pin-vender-fly-en-iman-no-esperar-estiramiento]].

## SPX 4 FLIES POSICIONALES — vigilancia persistente (Tania pidió monitoreo de salida 22-sep)
> Fuente: registro Tito + `API/posiciones.json` (id `SPX-FLIES-4-VENCIMIENTOS`). Vigila la tarea **WBJ Monitor Posiciones** (cada 10min, 9:30–16:15, email en cada cruce). TODAS son bajistas (cuerpo debajo del spot); con SPX 7781 están en rojo/hedge y pagan solo si SPX BAJA hacia su cuerpo. γ+ = contención = tiende a sangrarlas.

| Vto | Patas (cuerpo) | Crédito | Pérd.máx | Nivel de salida | GTC |
|---|---|---|---|---|---|
| **Sep30** | 7490/**7500**/7525 (BW) | $2,220 | ~$280 | cobra en cuerpo 7500; si sigue arriba 8 días, cortar por residuo | — |
| **Oct16** | 7650/**7700**/7750 | $4,685 | ~$315 | **COBRAR en 7700** (máx gan.), maxpain ~7660 | BTC **40.00** (+$685) |
| **Oct30** | 7250/**7400**/7550 (hedge) | $13,930 | ~$1,070 | 7625=empieza a valer · 7500=cobra 20-30% · **7400=CERRAR** | — |
| **Dec18** | 7475/**7500**/7525 | $2,435 | ~$65 | hedge barato, tiempo a favor, dejar correr | — |

Escalera de aviso (SPX cae hacia los cuerpos): **7700**(Oct16) → **7625**(flip Oct30) → **7525**(ancla) → **7500**(Sep30+Dec18) → **7400**(Oct30 cerrar). Aviso arriba: **7800** = tesis bajista alejándose. NOTA (RESUELTO 2026-09-22): antes el monitor cotizaba el precio de la ACCIÓN de MARA/PLTR LEAP como mark de la opción → falsos "IDEAL +50%". Corregido `simbolo_schwab` a OSI (`MARA  270115C00008000`, `PLTR  271217C00135000`, mismo formato que IREN). Verificado: ahora cotiza la OPCIÓN (MARA C8 mark $5.88 = +48.7% real; PLTR C135 mark $74.78 = +41.2% real).

## ✅ CERRADA 22-sep ~2:15pm ET — iron fly 7750 (defensiva, P/L −$185)
> Vendió 11.85, cerró **13.70** = **−$185 bruto** (~−$190 con fees). Motivo: el pin/closeTarget/callWall/putWall MIGRARON 7755→**7775** (spot rally 7759→7771, γ+ fuerte 17.9B) = invalidación del destino 7750. Cortó a −$185 vs pérd.máx −$315 (salvó ~$130). Disciplina correcta. LECCIÓN: entró con spot 7764 ya ARRIBA del BE alto 7761.85 (pin_estable dio CUIDADO al entrar) apostando reversión; la tendencia persistió y el imán la siguió. Registrada cierre en Tito. **Monitores de sesión: ya no aplican (posición cerrada).** Tania tiene sus 4 contratos libres de nuevo.

## ~~POSICIÓN 0DTE ABIERTA (22-sep) — iron fly 7750 + su manejo~~ (CERRADA, ver arriba)
- **EJECUTADA ~10:49 ET.** Iron fly cuerpo **7750**, alas **7735/7765** (±15). Crédito **$1,185** (fill 11.85), pérd.máx **$315**, ratio 3.76. **BE 7738.15 / 7761.85.** Registrada Tito #49. Cuerpo en VS3D mega-verde +4451 (destino), entrada lejos (spot 7763). Vto HOY.
- **CIERRE: GTC Buy-to-Close en 5.90 puesto en Schwab** (= +$592, 50%). Cobra el take-profit solo. (Alternativas que dimos: 4.75=+$710/60%, 3.55=+$830/70%.)
- **Líneas defensivas (lo que el GTC NO cubre):** ABAJO pierde **flip 7739.5** (=BE bajo) → γ negativo, cerrar defensivo antes de −$315. ARRIBA rompe **7765** (BE alto 7761.85) rumbo techo 7783/magnet 7785 = en contra.
- **Monitor task bmv0zhlhs** (`scratchpad/watch_pin_7755.py`, cada 45s): DOBLE — (1) defensa del 7750 fly (peligro real: <7741 flip / >7778 techo), (2) caza 2 ENTRADAS nuevas para los 3 contratos libres: 7783 rechazo→fly cuerpo 7755 desde arriba, 7740 rebote→fly cuerpo 7750 desde abajo. PIN=7747-7757. Expira ~30min → re-armar. (Umbrales subidos: ya no alarma en wobbles de 7766.)
- **Update 13:40 ET:** spot bajó a 7759 (dentro del tent), straddle crushó 18.35→12.60. Fly mark real **10.50** = P/L **+$135**; GTC 5.90 falta -4.60 (paga tarde, crush acelera 2-3pm). VS3D fresco: imán 7750 verde-monstruo, Gradient Gamma+Charm (simulación Roos) cierra el cono ~7758-7760 = resolviendo al pin. Nancy 7775 DESCARTADA por Tania (chocaba con 7750 + VS3D rojo en 7770). Espacio para 3 contratos más (alta prob only).

## Métodos que deben estar vigilados HOY (0DTE / intradía)
> γ+ de vuelta → día de PIN. Plan base: fly en el imán (~7700–7710) cuando asiente, ANTICIPAR el rebote en el piso 7674/72 (toque+giro) para entrar barato. Falta confirmar MS-flow + VIX (Tito down) antes de dar el strike. No perseguir; clavar en el toque de banda.

| Método | Regla de entrada (DISTINTA — no mezclar) | Trigger / niveles | Email vigilante (persistente) | Estado |
|---|---|---|---|---|
| **NANCY** | imán=VWAP; entrada=DS1(±1σ); gatillo=**DOBLE piso/techo**; cuerpo=VWAP | VWAP al abrir (viejo 7591 stale) | `watch_nancy_vwap_ds1.py` (tarea WBJ Nancy VWAP DS1) | esperar VWAP real del open |
| **SS (maestra)** | imán=nivel RETORNO (Tito); gatillo=precio **~20pt lejos**; cruces | imán ~7700, banda [7675,7719] | `watch_straddle_vs_spot.py` (tarea WBJ Straddle vs Spot) | spot 7697 pegado al imán, falta estiramiento a la banda |
| **PIN 0DTE / fly** | γ+; fly en el pin (cuerpo 7700) — usar ±15 (7715/7700/7685), NO ±20 (pérdida $748>regla) | pin 7700, techo 7716/7719, piso 7680/7672 | `watch_pin_0dte_fly.py` (tarea Vigilar Pin 0DTE, ventana 11:15-13:00) + **monitor combinado mon_all (task boguhnw7l)** | ✅ **EJECUTADA ~10:55** — iron fly **7685/7700/7715**, crédito **$13.15 ($1,315)**, pérd.máx ~$185, vto HOY. Registrada Tito #44. Entró spot ~7720 (borde alto), fade al pin 7700. **SALIDA: cobrar 50-70% (~$650-900) O dejar pinear al cierre 4PM.** BE 7687-7713. Manejo por monitor SPX pin (techo 7714≈ala alta, piso 7684≈ala baja, centro=pinando). |

## Posiciones con vigilancia HOY (además del pin SPX)
- **MARA LEAP C8 ene-2027** (costo 3.95, mark TS **6.00 = +52%**). Spot 13.72, γ+, rompió 13.5. Zonas: callWall MS **14.0**, Gann **14.34**, target 18; imán 13, maxpain 12, putwall/flip 11. **Orden de cierre PUESTA a 6.60** (≈ underlying 14.34). Plan: cobra si se topa 14.0–14.34; holdea por 18 si rompe+sostiene 14.34; defensivo si pierde 13. Monitor combinado **mon_all (task boguhnw7l)** avisa acercamiento a 14.34 / ruptura>14.45 / pérdida de 13. Tania quiere aviso si va a subir más para cancelar/subir el 6.60.
- **HIMS 40C vto 15-ene-2027** (costo 25.00, mark **2.06 = −92%**, deep OTM, ~4 meses al vto). Spot 28.56, γ+, tope call wall MS **30** (Gann 30). Necesita +40% al strike; theta acelera + IV 118% (crush). Lectura: salida con MENOS pérdida = pop a **30**; recuperación real = escalera Gann 34→37→40 (baja prob); corte defensivo = pierde flip **25.4**. NO promediar. Monitor combinado **mon_all (task boguhnw7l)** avisa pop 30 / escalera 34+ / pérdida 25.4.
- **META 1430C vto 15-ene-2027** (costo 8.65, ~−5%, spot 712). Call de LOTERÍA/convexidad (strike 2x spot, +101% al strike = inalcanzable). Recupera solo con up-move GRANDE + IV (catalizador = earnings META). Zonas: callWall **715** (tope), imán 700, piso 670/674 (flip). Salida menos pérdida: vender el pop si rompe 715 con fuerza; si rechaza→cerca de BE antes del sangrado (theta+IV). Revisar BID real (spread ancho). Monitor en vivo NO armado (Tania eligió solo el recordatorio). ✅ **Recordatorio programado: tarea Windows "WBJ Recordatorio META 1430C", one-time 26-oct-2026 09:35** (víspera earning) → email para cobrar en la rampa de IV antes del crush. Script `scripts/vigilante_spx/recordatorio_meta_1430c.py`.

- **✅ EJECUTADA — SPX IRON FLY BAJISTA Oct-30** (Schwab, 21-sep ~10:45, spot entrada 7719.76). Legs **7250/7400/7400/7550** (cuerpo 7400 ±150), **crédito $13,930.12**, **pérdida máx $1,065**, ratio 13:1. Registrada en Tito (#43). Tesis: seguro/hedge, paga si SPX VISITA 7500/7415 (P touch ~60-77%), cobrar 20-30% y cerrar temprano. OJO: entró con SPX 7719 (arriba del ala 7550) → hoy está cerca de máx-pérdida en mark; **el valor llega si SPX CAE**. Manejo (monitor **boguhnw7l** = "SPXFLY"): pierde 7650→**7625 flip** = empieza a valer; **7500** = zona ganancia (cobrar 20-30%); **7400** = cerrar (no esperar pin); 7725+ = más rojo, paciencia. Contexto contrario: γ+ hoy (contención). Vigilante de entrada `watch_entrada_fly_oct30_bajista.py` ya cumplió (posición tomada).

## Herramientas NUEVAS del núcleo (Roos/VS3D — correr SIEMPRE)
- **`scripts/flip_level.py [SYM]`** — nivel de REBOTE (abajo) y RECHAZO (arriba) por confluencia
  (gamma flip + put/call wall + $Value VS3D + Gann). = dónde el MM pasa de vender↔comprar.
  Correr al anticipar entrada/salida. (Necesita VS3D fresco de Tania.)
- **`scripts/pin_estable.py [--live]`** — GUARDIÁN anti-engaño: BLOQUEA el fly si el precio se ALEJA
  del pin durable (tendencia/melt-up) o el imán migra. Correr ANTES de vender cualquier fly de pin.
- **`scripts/gamma_expansion.py`** — tracker: 3 cierres γ≤0 seguidos → rango ~6% (tarea diaria
  "WBJ Tracker Expansion Gamma" 16:10, avisa por email). Si dispara: NO vender prima, favorece hedge.
- **INTEGRACIONES (aditivas):** flip_level ahora sale en el arranque (`estado_sistema.py` §9) + tiene gate de frescura VS3D · el monitor `mon_all` avisa ANTI-FADE en vivo (4 spots monótonos, neto>12pt = tendencia → no fly) · GATE corre la capa Roos solo.
- **⭐ `scripts/selector_metodo.py` — SELECTOR DEL MÉTODO DEL DÍA** (condición→método→setups ejecutables). Cableado en `estado_sistema.py` §10 → **SALE SOLO en el "buenos días"**. SIEMPRE da ≥1 trade con gatillo (γ+ estable=fly; tendencia=direccional/vertical; rebote=flip; γ−=direccional; cierre=settle). **REGLA: entregar los setups, no solo mostrarlos. SIN TRADES NO EXISTIMOS.**

## Reglas duras al disparar (cualquiera)
1. Verificar γ+/neutral + MS + Gann + VS3D ANTES de dar el strike (no a ciegas).
2. NO mezclar SS y Nancy. Si dudo cuál, PREGUNTO.
3. Dar el strike CLARO (cuerpo + alas + fade), no "entra ahora" vago.
4. Antes de "cierra": verificar núcleo + asimetría.
5. **Antes de vender un FLY de pin: correr `pin_estable.py` — si BLOQUEA (precio se aleja del pin), NO vender.**
6. **Para entradas/salidas de rebote: correr `flip_level.py` — el flip de mayor confluencia es el nivel mecánico.**
7. **GATE ya integra la capa Roos** (`verificar_trade.py` corre pin_estable + flip_level solo, aditivo). **Backtest propio (`backtest_pin.py`): fade-al-pin 92% base; cerca del pin <15pt = 100%, estirado 15-30pt = 50% → VENDER el fly solo con spot <15pt del pin.**

## Watches en pausa / retirados
- Oct30 fly bajista: **YA EJECUTADA 21-sep** (ver arriba en Posiciones). El vigilante de entrada cumplió; ahora es manejo vía monitor SPXFLY.
