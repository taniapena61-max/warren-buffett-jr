# Errores y lecciones

Registro cronológico de sesgos detectados y correcciones aplicadas.
Formato: fecha · qué se creyó · qué pasó · qué se cambia.

## 2026-09-01 · DELL earnings — veté un setup de manual ("un loto")

- **Qué creí:** le dije a Tania que NO entrara DELL antes del earnings, que era "un
  loto" (apuesta). Me dejé llevar por el contexto MACRO bajista del día (VIX subiendo,
  SPX gamma−, DELL cayendo −30 hacia el cierre) y lo trate como riesgo de lotería.
- **Qué pasó:** DELL reportó 1-sep AMC un BEAT enorme (EPS $7.04 vs 2.32, guía FY $192B)
  y abrió **+10%** el 2-sep. Era **un setup de MANUAL** del método de earnings de Tania:
  empresa fuerte (AI/servers), **desde soporte** (cierre 425 = mínimo 424–434), **IV
  inflada**, espacio arriba → movimiento tamaño-earning → **IV crush paga**. Ver
  `tesis/DELL.md`.
- **Qué se cambia (reglas):**
  1. **El método de earnings es un SISTEMA SEPARADO** del régimen del SPX/VIX/gamma. NO
     vetar una entrada de earnings de un solo nombre porque el índice se vea bajista.
     (Igual que 0DTE vs confluencia son sistemas separados.)
  2. **La caída pre-earnings hacia el cierre NO descalifica — ES el setup.** Entrar al
     cierre en el soporte con IV en su pico es exactamente lo que dice el método.
  3. **Si el checklist pasa (nombre fuerte · soporte · espacio arriba · IVR alta · skew
     call), PROPONER la entrada** con estructura. La CONFIANZA baja NO convierte un
     setup válido en "no entrar" — se propone con la salvedad, no se veta.
  4. **"un loto" queda PROHIBIDO como veredicto** salvo que falle el checklist con
     evidencia (sin soporte, IV no inflada, o movimiento esperado "normal" tipo SNDK).
- **Efecto:** montado el vigilante de earnings ([[metodo-earnings-volatilidad]],
  `scripts/vigilante_spx/watch_earnings.py`) que aplica el checklist + lentes + OI
  build-up y AVISA la entrada. Ver también `estudio-vix-settlement-miercoles`.

## 2026-09-02 · AMZN iron fly 255 — cuerpo ENCIMA del precio (trade autocontradictorio)

- **Qué hice mal:** propuse una iron fly neutral con el cuerpo (strikes de VENTA) en **255
  = exactamente el precio**, vto Sep-18 (16 DTE). Eso apuesta a que AMZN **NO se mueve en
  16 días** — y mis PROPIOS lentes decían lo contrario (IVR 98 = mercado precia movimiento
  grande ±15-21 pts, netGEX +0.14B = pin DÉBIL, cayó 12 pts en 3 días = en movimiento).
  **Trade que se contradice solo.** Además di P(ganar) ~60% cuando era de UN lado; la real
  (banda 249-261) es ~22-32%. Tania lo cazó: "el strike de venta está donde está el precio,
  o sea según tú AMZN no se mueve".
- **Reglas violadas:** (1) [[centrar-fly-en-destino-no-en-precio]] / "posicionarse LEJOS del
  strike de venta" ([[criterios-entrada-riesgo-credito]]) — puse el corto ENCIMA del precio.
  (2) [[regimen-primero-direccional-vs-pin]] — una fly de PIN necesita PIN (IV baja + gamma
  fuerte + consolidación); AMZN tenía lo contrario. (3) [[entrada-y-salida-verificadas-con-lentes]]
  — no verifiqué la coherencia estructura↔lentes.
- **Lección dura:** una fly/venta con el cuerpo AL precio SOLO vale con **PIN FUERTE** (tipo
  SPX netGEX +16.8B, IV baja). En nombres de IV alta / gamma débil / en movimiento es
  perdedora. Y si para tener alta prob hay que vender LEJOS pero eso da crédito<<pérdida
  (viola crédito>pérdida), entonces **NO HAY TRADE → esperar**. Las dos metas (perfil
  crédito>pérdida + alta prob) no siempre coexisten; cuando no, no se fuerza. El mejor
  trade puede ser NO trade. Verificar SIEMPRE que la estructura sea coherente con los
  lentes ANTES de darla.

## 2026-09-03 · Slate earnings 2-sep AMC — saltar todo fue CORRECTO (acierto validado)

- **Qué dije (2-sep ~3:40 PM):** SALTAR TODO el slate (AVGO, SNOW, HPE, NTAP, FIVE, PVH).
  Razón: IV comprimida (IVR 10–45), sin crush que cobrar; ninguno pasó el checklist.
- **Qué pasó (3-sep):** SNOW **+22.1%** (beat + guía subida, rip de IA), HPE **−7.7%**,
  AVGO **−6.7%** (beat pero guía Q4 floja), NTAP/FIVE planos, PVH −1.3%. Ver
  `historial/earnings_skip_2026-09-02.md` (rendición de cuentas completa).
- **Veredicto:** ACIERTO. El método vende IV inflada para cobrar el crush; con IVR baja
  el colchón de prima es delgado. Los 3 grandes (SNOW/AVGO/HPE) habrían **atravesado**
  esa prima delgada = pérdida. Saltar preservó capital y no cedió nada real.
- **Lección dura (nueva):** **IVR baja ≠ movimiento chico.** SNOW +22% con IVR 10. El
  riesgo de vender prima barata en earnings no es que "no se mueva" — es que te pagan
  POCO por cargar la MISMA cola gorda. Refuerza [[no-vender-prima-en-semana-earnings]]
  y [[metodo-earnings-volatilidad]]: sin IV inflada NO se vende, aunque parezca quieto.
- **Contraste con DELL (1-sep):** el sesgo NO es "siempre saltar earnings" ni "siempre
  entrar". Es el CHECKLIST: DELL sí pasó (IV inflada, desde soporte) → entrar; este slate
  no pasó (IV comprimida) → saltar. El método discrimina por evidencia, no por ánimo.

## 2026-09-03 · Perdí la entrada 0DTE por decirle "espera el pin asentado (tarde)"

- **Qué hice mal:** en la mañana le dije a Tania que la mariposa 0DTE "espera la tarde,
  12-2:30, al pin asentado". Cuando volvió a las 2:10 PM le dije "ya pasó el crush". La
  mandé a esperar y para cuando llegó **ya no había prima**. Whipsaw. Se frustró con razón.
- **El error de método:** la mariposa 0DTE se VENDE cuando el pin se **ESTÁ FORMANDO y la
  prima AÚN está gorda (~11:30-13:00)** — el crush que te paga ocurre POR LA TARDE mientras
  la posición corre. Esperar al pin "asentado" (2pm) = vender **después** del crush = prima
  en centavos con riesgo gordo (ese día el straddle cayó $22.70→$9.40; a las 2:10 el GATE
  vetó TODO por crédito<<pérdida). En 0DTE **el crush es la SALIDA, no la entrada**
  ([[sistemas-separados-0dte-vs-confluencia]], [[griegos-reloj-intradia-0dte]]).
- **Bug del vigilante (corregido):** esperaba que magnet≈maxpain **convergieran** (|dif|≤15).
  Ese día el imán se asentó en 7750 y el maxpain se quedó en 7665 (85 pts) → NUNCA
  convergieron → NUNCA avisó. El pin real = **imán ESTABLE** (mismo valor N lecturas), no la
  convergencia con maxpain. Reescrito `watch_pin_0dte_fly.py`: ventana **11:15-13:00**,
  dispara cuando imán estable + gamma+ + GATE pasa, y avisa "VENDE YA si el straddle sigue
  gordo". Ver [[vigilante-pin-0dte-tarde]].
- **Regla nueva:** la ventana de VENTA del fly 0DTE es **pin formándose + straddle aún gordo
  (>~$13)**, no "pin asentado". Si Tania llega con el straddle ya crusheado (<~$10), la
  respuesta honesta es **ya pasó, no fuerces centavos** — y anticiparlo la próxima con el
  rastreo del grid MM ([[rastreo-grid-mm-diario]]).

## 2026-09-11 · ORCL fly — le prometí un cierre de $530 en la mañana que no existía

- **Qué creí:** con el fly ORCL 157.5/165/172.5 (0DTE) y ORCL gapeando a 164.7 (justo en el
  cuerpo 165), estimé que al abrir la IV de earnings se colapsaría y el fly valdría ~1.8-2.5
  para recomprar → neto ~$430-500 en la mañana. Le dije a Tania que su meta de $530 era
  alcanzable temprano.
- **Qué pasó:** al abrir el fly valía **~5.15-5.68** (neto solo **+$115-168**), NO ~2. El
  straddle 0DTE seguía **gordísimo (~8)** porque ORCL, un día después de un gap de 7%, tenía
  **vol intradía enorme** (el mercado priceaba ~±8 pts para el día). Subestimé el residual de
  IV/vol el día-1 post-earnings. Tania cerró defensiva cuando ORCL empezó a caer hacia el BE
  bajo — decisión correcta. **Fill real = 5.80 → neto +$103** (Tania puso GTC a 5.80, no la vio,
  la re-hizo a 6.04; la de 6.04 salió REJECTED y llenó la de 5.80). Canté el P&L DOS veces mal
  antes de saberlo (+$168 con el "precio para cerrar" 5.15, luego +$79 con 6.04). Lección dura:
  **no cantar P&L hasta que Tania confirme el FILL real** — ni el "precio para cerrar" del broker
  ni la última orden enviada sirven; puede haber órdenes duplicadas o rejected.
- **El error de método (mismo patrón que [[fly-gana-en-el-movimiento-no-en-el-pin]] y el
  error del 2026-09-03):** el precio en el cuerpo NO hace que el fly valga su máximo — eso
  solo pasa cuando **el theta quema el straddle**. Con el straddle en $8 por la mañana, el fly
  vale ~5 aunque ORCL esté clavado en 165. Los ~$500 requieren la **compresión de la tarde**
  ([[metodo-cierre-fly-en-el-settle]], [[odte-fly-tarde-pin-asentado]]). Prometí un número de
  mañana que dependía de una compresión de tarde. Contradicción.
- **Peor aún:** di una estimación de valor del fly (1.8-2.5) **sin mids reales** — pre-mercado
  MS da 0 y Schwab da el quote PEGADO de ayer ([[fmp-quote-stale-en-earnings]]). No tenía base
  para ese número.
- **Regla nueva:** NUNCA prometer un valor de recompra de un fly 0DTE post-earnings desde
  pre-mercado. Día-1 post-earnings el straddle 0DTE se queda gordo por vol intradía; el valor
  del fly se realiza con el **theta de la tarde**, no con el precio en el cuerpo. Si la meta de
  ganancia es alta (>70% del máx), decir claro: **"eso vive en la tarde"** — y contrastar con
  el hard-to-borrow que igual fuerza cierre ~2:30-2:45. Esperar el mid REAL post-apertura antes
  de dar cualquier número de cierre.

## 2026-09-11 · SPX fly de cierre — cuerpo alto vs el pin + Tito re-apuntó intradía

- **Qué pasó:** entramos fly 7660/7675/7690 (cuerpo 7675 = closeTarget de Tito) al rechazo del techo ~11:50AM. Toda la tarde el precio pineó **7667**, NO 7675 — el techo 7673.75 rechazó 7675 ~5 veces. La fly quedó **mis-centrada arriba** (cuerpo 8 pts sobre el pin real). Máx intradía +$253. A las 2:44PM **Tito re-apuntó closeTarget/magnet 7675→7660** (debajo del BE 7664.77) y el precio cayó al BE → cambio de régimen real → cerramos en verde **+$80** antes de voltearse (7660 = −$475 máx).
- **Contraste con Nancy (compañera de Tania, la de los cierres):** ella centró en **7665 = el pin/maxpain real** (donde clavaba el precio) → +$396 y cómoda. Mismo día, mismo modelo, mejor centrado = mejor resultado.
- **Lección 1 (centrado):** centrar el fly de cierre en el **PIN/maxpain donde el precio REALMENTE pinea** (leer el tape + rangeClose centro), NO en el tope del closeTarget de Tito. Si el techo rechaza un strike todo el día, el settle resuelve DEBAJO — cuerpo ahí. [[vertical-rapido-rechazo-resistencia]] [[checklist-anticipatorio-orden-de-cierre]]
- **Lección 2 (Tito dinámico):** el closeTarget de Tito **se mueve intradía** (7650→7660→7675→7660). No es fijo. Monitorearlo: si re-apunta debajo de tu BE = señal de salida.
- **Lección 3 (ejecución):** en un cierre que se deteriora, **ejecutar RÁPIDO** — alerté a 8.70 (+$155), el fill fue 9.40 (+$80) por seguir cayendo 1-2 min. El slippage se come la ganancia.

## 2026-09-11 · Salté un fly de cierre +EV por el ratio 0.8:1 — habría ganado +$205

- **Qué pasó:** ~3:15PM recomendé el fly de cierre 7650/7660/7670 (cuerpo=maxpain 7660, bien centrado). A las 3:31 el straddle crushó a 5.08 → el ±10 daba crédito 4.43 / pérdida 5.57 (ratio 0.8:1) → **dije "skip" porque viola crédito>pérdida.** Tania lo vio a crédito ~5.15 y **cerró en 3.10 = habría sido +$205.** El pin aguantó (cerró ~7662-63, dentro). La salté por conservador.
- **La contradicción:** minutos antes YO MISMO calculé que el ±10 era **+EV (~+$100-200)** con el pin casi seguro. Luego dejé que la regla "crédito>pérdida" me hiciera "skip" — cambié mi lectura correcta por la regla literal.
- **Regla nueva / EXCEPCIÓN codificada:** la regla **"crédito > pérdida"** es para flies que se ABREN con HORAS por correr (riesgo de movimiento). En un **fly de CIERRE al wire** (poco tiempo + γ+ fuerte + pin clavado), un ratio **~1:1 (o levemente peor) es ACEPTABLE** porque la **PROBABILIDAD (~70%+) carga el ratio flaco → +EV.** Es EXACTAMENTE como ganan las compañeras a diario: toman el pin de alta probabilidad, NO lo saltan por el ratio.
- **Para mí:** en el cierre, calcular **P(dentro) × premio vs P(fuera) × pérdida (EV)**, no vetar por el ratio. Si el EV es positivo y el pin está clavado, DAR la entrada (la decisión es de Tania, no bloquearla). [[gate-demasiado-rigido-nunca-entra]] [[metodo-cierre-fly-en-el-settle]] [[cuerpo-fly-cierre-en-maxpain-no-callwall]]

## 2026-09-16 · Día FOMC — 4 errores del mismo patrón: describir en vez de entregar

- **Error 1 (P&L mal calculado — BWB Sep-30):** dije "está en pérdida máxima (~$280)"
  solo porque spot estaba arriba del ala 7525, sin contar que quedaban 14 DTE de valor
  extrínseco cubriendo la posición. Tania corrigió con el broker (+0.41%). Recalculado
  bien: +$265, no pérdida. **Regla:** con DTE>0, "spot pasó el ala" NO es "pérdida
  máxima" — hay que restar el valor extrínseco real (marks del broker), nunca asumir
  intrínseco puro salvo 0DTE al cierre. Mismo patrón que el P&L de ORCL (11-sep): no
  cantar un número sin el mark real.
- **Error 2 (gamma = veto, no liquidez):** a las 15:39-15:47, pin migrando a 7540 +
  straddle desinflándose $50→$13 = confirmación completa del método CIERRE (Carly).
  Traté "netGEX sigue negativo" como razón para NO dar la fly y me quedé debatiendo si
  el rebote era "ruido". Carly es textual: **"gamma = liquidez, NO dirección."** La fly
  7540/7550/7560 simulada después dio +$462.50 (+63%) en minutos. **Regla:** pin+straddle-
  crush en los últimos 15-30 min = dar la fly YA, el régimen es nota de riesgo, no veto.
  Ver `metodo-cierre-dar-la-fly-no-solo-describirla` (memoria Claude).
- **Error 3 (creé un vigilante duplicado):** escribí `watch_nancy_vwap_ds1.py` sin
  revisar `scripts/vigilante_spx/` primero — ya existían ~20 vigilantes, incluido
  `watch_settle_nancy.py` (14-sep) y `watch_straddle_vs_spot.py` cubriendo métodos
  relacionados. **Regla:** `ls scripts/vigilante_spx/` SIEMPRE antes de escribir un
  `watch_*.py` nuevo — casi seguro ya existe.
- **Error 4 (mezclé dos métodos de clase):** propuse una sola tarea "Nancy+cierre"
  fusionando el método de la maestra (straddle-vs-spot, zona imán a ojo) con el de
  Nancy (VWAP+DS1+doble techo/piso) como si fueran lo mismo, y le atribuí el VWAP a la
  maestra cuando es la precisión de Nancy sobre el concepto vago de la maestra. Tania
  lo notó dos veces seguidas y preguntó si había "olvidado la clase". **Regla:** releer
  el .md de Escuela/ en el momento antes de afirmar de qué trata un método — no citar
  de memoria de la sesión, aunque se haya leído bien hace horas. Nunca fusionar dos
  métodos en una tarea sin que Tania lo pida.
- **Efecto:** creadas 5 tareas programadas (Lun-Vie), una por método — apertura
  delta (9:42am), SS/maestra (11:02am), Nancy DS1 (12:55pm), cierre/Carly (2:04pm),
  overnight (3:48pm) — cada una cita el método exacto y usa los `watch_*.py` que ya
  existían. Meta de Tania: "que cada día podamos dejar un overnight" + revisar
  errores para no repetirlos — este bloque es esa revisión.

## 2026-09-16 · No usar `source API/.env` — filtra otros secretos al output de bash

- **Qué pasó:** para mandar el email de rendición de earnings vía Resend hice `source API/.env`
  para cargar `RESEND_API_KEY`. El archivo tiene otras líneas (nombre con espacio sin comillas,
  una cookie larga `intercom-session-...`) que bash interpretó como comandos/tokens → los
  errores de "command not found" **imprimieron fragmentos de esas otras líneas** (incluyendo un
  valor de sesión) en el output de la herramienta. La regla del proyecto es **nunca imprimir el
  contenido de `API/`**, y `source` sobre un `.env` no garantizado 100% "KEY=VALUE limpio" lo
  viola indirectamente vía los mensajes de error del shell.
- **Regla nueva:** para extraer UNA variable de `API/.env`, usar `grep '^VAR_NAME=' API/.env |
  cut -d= -f2-` (o similar) y exportarla a mano — nunca `source`/`set -a; source; set +a` sobre
  el archivo completo. Eso evita que bash intente ejecutar/interpretar líneas que no controlo.

## 2026-09-22 — Fly 7750 0DTE: entrar arriba del BE apostando reversión (pin migró)
- **Trade:** iron fly cuerpo 7750 (alas 7735/7765), vendido 11.85 con spot 7764 = YA arriba
  del BE alto 7761.85. Tesis: reversión abajo al imán 7750 (VS3D mega-verde). Cerrado
  defensivo a 13.70 = **−$185** cuando pin/closeTarget/callWall/putWall migraron 7755→7775
  (γ+ fuerte, spot rally). Salvó ~$130 vs la pérd.máx −$315.
- **La señal que se subestimó:** al entrar, `pin_estable` dio **CUIDADO** (imán saltando
  7755↔7785, "esperar que asiente") y el spot ya estaba en/arriba del BE. Eso era el aviso.
- **Lección:** cuando el precio ya está ARRIBA del BE alto al momento de vender el fly
  (entrada "desde arriba" apostando reversión), si la tendencia PERSISTE el imán la sigue y
  la tesis muere — su propio método lo advierte ("contrarian funciona hasta que la tendencia
  persiste"). Regla: si `pin_estable`=CUIDADO Y spot fuera del BE → NO forzar; esperar el
  toque+giro del extremo (7740/7783) para entrar LEJOS de verdad, no a medio camino.
  Ver [[dia-de-pin-vender-fly-en-iman-no-esperar-estiramiento]], [[anticipar-proteger-ganancia-antes-de-catalizador]].
