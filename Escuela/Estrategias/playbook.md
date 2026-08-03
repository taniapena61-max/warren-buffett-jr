# Playbook de estrategias — Tania (para practicar en DEMO)

> Estrategias derivadas de **tus propias clases** (Curva del SPX, Iron Butterfly,
> Verticales Vendidos, VS3D, Gann) y de tu estilo documentado: **posicionarte EN
> el imán**, no lejos; **crédito > pérdida máxima**; gestión > setup.
>
> ⚠️ Esto es **material de práctica y research, no asesoría**. Se prueba en DEMO.
> No ejecuto órdenes. Cada operación va al [registro de demo](registro-demo.md)
> para ver qué funciona y qué mejorar.

---

## Marco común (de la clase "La Curva del SPX")

Antes de cualquier estrategia, ubicar 3 cosas del día (de la cadena de Schwab):
- **Gamma Flip** = la línea de calma. **Encima** = mercado tranquilo (el dealer
  amortigua, el precio se pega al imán) → favorece vender el centro. **Debajo** =
  nervioso (amplifica) → cuidado, mejor no vender el centro.
- **Call Wall** (techo) y **Put Wall** (suelo) = dónde el dealer frena/sostiene.
- **Straddle** = ancho esperado del día. **Deltas .20/.25/.30** = probabilidad.

Regla que gobierna todo (Natenberg, tu clase): *no operas el precio, operas la
diferencia entre tu campana y la del mercado.*

---

## E1 · Iron Butterfly en el imán (SPX, corto DTE) — TU JUGADA INSIGNIA

**Tesis:** el precio muere cerca del imán (Gann Cardinal + pin de gamma + POC).
De la clase de la curva: en mercado tranquilo (sobre el Gamma Flip) el precio se
pega al pico de la campana.

**Cuándo entra — CONFLUENCIAS de la mariposa 0DTE (checklist, NO las 3 confluencias swing).**
Automatizado en `ruta_0dte` → campo `confluencia_mariposa` (6 factores):
1. SPX **sobre el Gamma Flip** (modo "imán": gamma+ contiene, se pega al pico).
2. **Gamma LOCAL pesada** = mercado lento / pin. **NO** en gamma fina/vacío (momentum).
   *[video VolSignals: gamma = VELOCIDAD; pesada frena, fina deja correr.]*
3. **Ventana 11 AM – 1 PM ET** (manda theta; menos movimientos bruscos).
4. **VIX no picando** (vol en calma; VIX picando = esperar).
5. **Volumen presente** (obligatorio, como toda entrada).
6. **Dirección al imán** ("va a subir") — lectura de dealer / Spot vs Straddle.
- Sin evento macro que rompa las alas ese día.
- **Salida:** el **crush del VIX** = toma de ganancia (la IV colapsó), junto al TP 50–70%.
- **Niveles de velocidad (video):** Call Wall = donde el mercado frena (ajusta target);
  Put Wall = soporte donde conviene **vender puts**, no comprarlos (no perseguir la baja).

**Estructura:** centro (vende call + vende put) en el imán; alas (compra call OTM
+ compra put OTM) **fuera del straddle del día**.
- **Tu regla:** crédito > 50% del ancho de las alas (crédito > pérdida máxima).
  Recordatorio honesto: eso implica **probabilidad de éxito < 50%** — lo aceptas
  a cambio de que cuando ganes, ganes más de lo que arriesgas.

**Gestión (de la clase Iron Butterfly):**
- **Take profit: 50–70% del crédito.** No esperar el máximo.
- **Zonas:** verde = cerca del centro; amarilla = cerca del BE; roja = cerca de un ala → decisión rápida.
- **Stop:** si rompe un BE y no vuelve, o si el delta se vuelve muy direccional.
- **Ajuste:** rolar el centro si el imán se desplazó; convertir a cóndor para ampliar rango.

**Invalidación:** SPX cruza el **Gamma Flip a la baja** (cambia a modo amplificar) →
la campana ya no se cumple sola; la mariposa deja de tener ventaja.

**Ejemplo con hoy (24-jul, SPX cerró 7411.98):** imán = 7410 (Gann −0.25 Cardinal
+ pin de gamma), straddle del día ~$30 (rango 7381–7442). Mariposa centrada 7410,
alas fuera de 7381/7442. Practicar en DEMO y anotar.

---

## E2 · Bull Put Spread ITM en la Put Wall (tu vertical contrario)

**Tesis:** vender el **seguro caro de la cola izquierda** cuando el miedo está
sobre-cobrado y hay soporte de confluencia debajo. De la clase de la curva:
*"Vender un Bull Put no es apostar a que suba; es apostar a que el miedo de esa
zona está cobrado de más."* **No** el bull put OTM lejano (la jugada de la
mayoría) — el **ITM/al nivel**, tu estilo: crédito grande, riesgo pequeño (ratio
hasta 8:2, de tu clase de Verticales).

**Cuándo entra:**
- Confluencia de **soporte** debajo (Put Wall + Gann + tu línea) que esperas aguante
- IV media-alta (primas jugosas)
- SPX sobre el Gamma Flip (soporte del dealer activo)

**Estructura:** vende put (en/sobre el nivel de soporte), compra put más abajo
(seguro). Crédito neto. Pérdida máx = ancho − crédito. BE = strike vendido − crédito.

**Gestión (clase Verticales):**
- **El extrínseco manda, no los días.** Vigila el valor extrínseco de la put
  vendida — cuando casi se agota estando ITM, sube el riesgo de asignación.
  (Esto es exactamente lo que aplicamos a tu IREN.)
- **Take profit:** 50% (o 20–30% si es muy ITM con crédito alto).
- DTE: 30–45 para dar aire; en SPX intradía, alinéalo con tu straddle.

**Invalidación:** cierre debajo de la Put Wall / del soporte de confluencia →
"desaparece el suelo justo en la zona nerviosa" (tu clase). Cerrar.

---

## E3 · Descuento bajo EMA200 (acciones, tu estrategia de swing)

**Tesis:** comprar calidad a descuento técnico (bajo la EMA de 200) y salir en +25%.

**Cuándo entra:** empresa con score de calidad ≥ 6.5/10 **y** precio bajo su EMA200
(el screener `discount_screen` ya filtra esto — evita las trampas de valor).

**Gestión:**
- **Salida:** +25% de apreciación (tu objetivo declarado).
- **Invalidación:** si la tesis fundamental se rompe (no solo el precio).
- **Tamaño:** ≤ 10% del capital por posición (tu límite de perfil).

**Herramienta:** ya construida — `discount_screen` en el motor. La corremos y las
candidatas van al registro de demo.

---

## 🚨 REGLA #0 — VOLUMEN OBLIGATORIO + NO MEZCLAR SISTEMAS (no negociable)

**Ninguna entrada sin volumen presente confirmando el nivel.** El volumen aplica a
**TODAS** las entradas (0DTE y swing). Sin volumen = falso movimiento (Wyckoff:
esfuerzo vs resultado; VS3D: "el volumen confirma o niega cada nivel").

**Pero hay DOS sistemas de entrada y NO se mezclan** (verificado en tus clases —
Gamma/Charm 0DTE, El Poder de Vanna, Wyckoff P3):

- **NO-0DTE (swing / posicional):** volumen **+ confluencia de las 3 lentes**
  (VS3D + MarketSnack + Gann apuntando al mismo strike). Marco Wyckoff (entrada
  estándar = confluencia multi-timeframe).
- **0DTE (mismo día, ej. mariposa):** volumen **+ lectura de dealer**
  (gamma/charm/straddle, Spot vs Straddle). Se **entra "cuando va a subir"**; el
  **crush del VIX es la SALIDA** (toma de ganancia: la IV colapsó). **Aquí NO se
  usan las 3 confluencias.**

La confluencia dice DÓNDE mirar; el volumen dice si es REAL. ⚠️ Nota: hoy
`wbj/confluencia.py` (`mapa_en_vivo`) aplica las 3 lentes a todo — sirve para el
sistema **swing**, NO para validar 0DTE. Pendiente separarlo por ruta.

## Reglas de oro que aplican a TODAS (tu perfil + tus clases)

1. **Tamaño:** ninguna posición > 10% del capital. En opciones, el riesgo es el
   100% de la prima/pérdida máxima definida.
2. **Plan de salida ANTES de entrar:** TP y SL definidos. "La clave no es el setup,
   es la gestión."
3. **Evita eventos** (earnings, macro) para las que venden prima corto plazo.
4. **La asignación se gestiona, no se teme** — vigila el extrínseco.
5. Cada trade de demo → al [registro](registro-demo.md), con qué esperabas y qué pasó.
