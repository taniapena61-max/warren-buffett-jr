# 🎥 VolSignals — "Dealer Hedging Dynamics" (TGIF, video YouTube) · resumen + extracción

> Video del canal **VolSignals** (los creadores de tu VS3D). Ponentes: **Dan**
> (ex-lead trader del S&P en Belvedere) y **Matt** (ex-market maker). Transcripción
> completa en `Materiales/clases/texto/VolSignals - Introduction to Dealer Hedging
> Dynamics (TGIF, video YouTube).txt`.

## Resumen (qué enseñan)
1. **El mercado no se mueve al azar: flujo → posiciones → hedging → movimiento.** El
   cliente que tradea una opción no la va a hedgear; la **posición neta** la carga el
   **market maker**, y su cobertura continua es lo que mueve el precio.
2. **"Lo que se tradeó" es clickbait** (Unusual Whales, Cheddar Flow). Cuando lo ves en
   la cinta, el impacto ya pasó. Lo que importa es el **HEDGING FLOW** (la cobertura).
3. **Mecánica del hedge (delta-neutral):** MM largo call → **vende futuros**; largo put →
   **compra futuros** (corto call → compra; corto put → vende). El delta es el 1er orden;
   luego la **cascada de riesgo: gamma → charm → vanna →** vega, term structure, skew.
4. **Es probabilístico, no determinista.** VS3D te da **drift** (tendencia del día) y
   **velocidad** (gamma). Nadie te dice dónde acaba exacto.

## 🎯 Extracción para NUESTRAS entradas (lo accionable)

### A. Confirma nuestra decisión del Gamma Flip (¡de la boca de los MM!)
Critican el **"naive gamma model"** (SpotGamma/Squeeze: asumir MM corto puts/largo
calls) como **erróneo hoy con 0DTE** — "garbage in, garbage out". VS3D usa **data REAL
de la CBOE** (sabe QUIÉN tiene cada posición). → **Exactamente por esto mi GEX de Schwab
es solo una ESTIMACIÓN etiquetada y VS3D manda.** Lo que codificamos está bien.

### B. Humildad con "gamma negativa" (refina mi GEX)
Matt: la gamma negativa **entrenchada es RARA**; lo que la gente lee como negativa suele
ser solo un **diferencial** (ej. normal +10B, hoy ~4B). → Cuando mi GEX diga "gamma
negativa/bajo el flip", tratarlo como **señal de régimen, no como hecho** — puede ser un
diferencial. Confirmar con VS3D. (Ajuste anotado en memoria.)

### C. GAMMA = VELOCIDAD (afina la mariposa y las entradas)
- **Gamma pesada = mercado LENTO** (el MM absorbe/contiene, "shadow order book"). →
  terreno de **pin / mariposa** (theta). Es lo que ya usamos como "modo imán".
- **Gamma fina = vacío**, el precio se mueve libre y **no necesita frenar** → NO poner
  mariposa ahí; es zona de momentum.
- **Call Wall** = de repente más gamma → esperar que el mercado **frene** ahí (ajustar
  target alcista). **Put Wall** = soporte equivalente abajo.

### D. Vender puts en soporte de gamma (corrobora tu Bull Put + el crush)
"Si hay mucha gamma/soporte abajo, **NO compres puts caros** esperando otro gran
rompimiento; ahí puede haber buen trade **VENDIENDO puts**" — mientras el resto entra en
pánico (CNBC "markets in turmoil"), tú sabes que hay gamma que sostiene. → Corrobora tu
**Bull Put ITM en la Put Wall** y el **"no perseguir la baja" del crush**.

### E. Drift de fin de día por el decay 0DTE (suma a nuestro reloj)
La posición 0DTE **decae a las 4 PM**; el MM la mantiene atada al mark-to-market → crea
el **drift de fin de día** (el "boundary" de VS3D). El tooltip **"hedge product to trade"**
dice cuántos futuros hay que mover; **crece al acercarse el cierre**. → Se suma a nuestro
reloj intradía (tarde = charm activa gamma + drift del decay).

## 🎨 Video 2 — El Gamma Profile (rojo/verde) y el MODO OPERATIVO

Segundo video de VolSignals, el manual del **gamma profile de tu VS3D** (el gradiente):
- **ROJO = gamma NEGATIVA** → mercado **errático**; el MM se pone más largo delta y
  **vende más futuros** al caer (o compra al subir) → **amplifica**, "te corre al book",
  NO da liquidez. El movimiento **no para** hasta salir a verde.
- **NEGRO = gamma neutral / ausente.**
- **VERDE = gamma POSITIVA/alta** → **estabilidad**; el MM absorbe, contiene, movimientos
  muted. La subida se **absorbe** (resistencia).
- El profile simula **todos los precios × tiempos del día** → predice comportamiento.

**Regla de confluencia (codificada en `modo_operativo`):**
- **VERDE (gamma+) → VENDER PRIMA** (mariposa/verticales); **fade** las extensiones (no
  esperes 40/50/60 pts en un largo, el MM largo gamma vende en la subida).
- **ROJO (gamma−) → COMPRAR opciones / momentum**; **NO vender prima**. Un reversal
  fuerte en gamma roja corre sin freno hasta llegar a verde. "Aquí las opciones SÍ rinden."
- Para futuros direccionales: si compras y el mercado **se aplana** (entró a verde) →
  puede ser hora de **salir** (te absorben).

> Esto **encaja perfecto** con nuestro sistema: la mariposa (vender prima) quiere VERDE;
> la ruta 0DTE ya trae `modo_operativo` y `gamma_local` que reflejan esto.

## Para repasar
- Pídeme *"examíname de este video"* o *"cruza esto con mi ruta 0DTE"*.
- Enlaza con [[La Curva del SPX]], [[El Poder de Vanna]], [[Gamma Charm y Market Makers 0DTE]].
