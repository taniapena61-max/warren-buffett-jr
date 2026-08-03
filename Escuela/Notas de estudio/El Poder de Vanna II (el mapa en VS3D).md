# 🌀 Vanna II — el mapa en pantalla (Parte 2)

> Continuación de **[El Poder de Vanna](El%20Poder%20de%20Vanna.md)** (Parte 1 = el motor).
> La Parte 1 explicó *por qué* la vol mueve el delta y el dealer compra sin querer.
> Esta parte da el **mapa**: dónde vive Vanna en el VS3D y cómo leerla junto a
> Gamma y Charm para sacar un veredicto operable.

## Recap del motor (en 4 pasos)
1. El dealer está **corto puts OTM** — el seguro que compran los fondos vive en la
   zona **25Δ**, justo donde Vanna pega más fuerte.
2. **El VIX se mueve** (el precio no ha hecho nada todavía): si cae, el delta de
   esos puts se encoge; si sube, se hincha.
3. El dealer **se cubre sí o sí**: vol abajo → recompra futuros → SPX deriva arriba.
   Vol arriba → vende futuros → la caída se acelera.
4. **El bucle se alimenta.** Asimetría cruel: hacia abajo empujan a la vez Vanna +
   Gamma negativo + fondos vol-control.

## Dónde vive Vanna en VS3D — 3 paneles, una historia
Vanna no tiene panel propio: **es la 4ª dimensión (el VIX)**. Los tres paneles son
una foto; el VIX decide hacia dónde se mueve esa foto.

| Panel | Qué es | Qué te dice |
|---|---|---|
| **Positions by Strike** | La **causa** | Dónde está la montaña de puts cortos = la munición de Vanna, strike por strike |
| **Gamma Profile** | El **régimen** | Contención (positivo) o amplificación (negativo): ¿el empuje encuentra freno o acelerador? |
| **Charm Profile** | El **reloj** | Cómo evoluciona la cobertura con las horas: cuándo el goteo del tiempo se suma o se resta al empuje de la vol |

## La munición — leer el pico de Vanna en *Positions by Strike*
- Busca la concentración de **puts cortos del dealer entre −3% y −7% del spot**:
  esa banda coincide con la zona **25Δ**, el pico de Vanna de Natenberg.
- Cuanto **más grande y más cercana** la montaña → más deltas se recolocan por
  cada punto de VIX → **más munición cargada**.
- Puts muy lejanos (<10Δ) aportan poco: su Vanna ya se desplomó a cero. La onda
  tiene pico y luego muere.
- **Ojo al lado call:** si los dealers están cortos calls OTM cercanas, parte del
  efecto se compensa. El **Vanna neto direccional nace del skew** → compara siempre
  los dos lados. *(Ver [Skew](Skew%20%E2%80%94%20la%20sonrisa%20torcida.md).)*

**Forma del perfil de Vanna por strike:** cero en ATM (ahí manda Gamma) · pico en
la zona 25Δ put (el inventario del dealer) · se apaga en las alas.

> Regla rápida: **montaña de puts grande + VIX con espacio para caer = viento de
> cola listo.** Montaña pequeña = motor sin gasolina.

## Munición × Volatilidad — los 4 cuadrantes de Vanna
| | **VIX cayendo** | **VIX subiendo** |
|---|---|---|
| **Montaña grande** | 🟢 **Viento de cola pleno.** Cada punto de VIX abajo obliga a recomprar futuros. Deriva alcista lenta y sin volumen: el terreno del vendedor de prima. | 🔴 **Máxima munición en contra.** Los deltas se hinchan a la vez, el dealer vende. Con Gamma negativo = la espiral de la Parte 1. |
| **Montaña pequeña** | ⚪ **Motor girando en vacío.** Vol baja pero casi no hay deltas que recolocar → derivas débiles. Típico de la semana post-OpEx. | 🟠 **Peligro subestimado.** Sin puts que sostener, el mercado está desnudo: la caída no tiene la red de recompras que suele frenarla. |

## Lectura conjunta — Vanna × régimen de Gamma
| | **Vanna a favor (arriba)** | **Vanna en contra (abajo)** |
|---|---|---|
| **Gamma positivo** | Deriva contenida: sube poco a poco y no corrige. **El mejor entorno del Bull Put Spread.** | El freno gana *de momento*: el Gamma contiene la venta, pero cada punto de VIX arriba erosiona el muro. **Vigila el flip point.** |
| **Gamma negativo** | **Rebote violento:** sin freno, el vol crush produce subidas verticales (los rallies de alivio tras el pico de miedo). | **La espiral completa.** Amplificación + venta obligada. Aquí no se vende prima: **se sobrevive.** |

## El reloj del día — la mañana es de Vanna, la tarde es de Charm
- **09:30–13:00 ET · manda VANNA.** La IV se reajusta tras la apertura; es cuando
  el VIX hace su recorrido. Si hay evento/dato, **el crush ocurre aquí.**
- **13:00–16:00 ET · manda CHARM.** Con el VIX asentado, el goteo del tiempo toma
  el relevo (charm de las 0DTE). La tarde está contaminada por flujos mecánicos:
  **no es información direccional.**
- **El día perfecto del vendedor de prima:** vol crush por la mañana (Vanna compra)
  + charm supresivo por la tarde (el rango aguanta). Doble viento de cola.

> Enlaza con [Griegos + reloj intradía 0DTE] de tus clases: mañana=Vanna,
> 11–13 ET=ventana mariposa, tarde=charm activa gamma.

## El día post-evento, paso a paso
1. **Víspera:** vol del evento inflada, montaña de puts cargada.
2. **Publicación:** el VIX se desinfla 2–4 puntos en minutos.
3. **Ventana 30–90 min:** la recompra del dealer empuja el SPX — **muchas veces en
   dirección contraria al titular.** No es opinión, es cobertura.

*(Secuencia típica de FOMC o CPI. Enlaza con tu lección [VIX cae el día después
de la noticia] y [Día FED: esperar la revalorización].)*

## Operativa — la secuencia matinal de Vanna en 5 pasos
1. **VIX y su curva:** ¿percentil? ¿contango o invertida? ¿evento hoy con vol
   inflada? → decide si el motor tiene recorrido.
2. **Positions by Strike:** mide la montaña (tamaño + distancia al spot) y compara
   el lado call → cuantificas la munición.
3. **Gamma Profile:** régimen y flip point → ¿freno (positivo) o acelerador (negativo)?
4. **Charm Profile:** ¿supresivo o direccional? → qué hará la tarde.
5. **El veredicto:** cuadrante de Vanna + régimen de Gamma + reloj de Charm = sesgo
   del día y estrategia. **Sin veredicto no hay trade.**

## Los 5 errores al leer Vanna en pantalla
- ❌ **Confundir Vanna con Gamma** (mirar solo el spot). Vanna se lee en el VIX;
  si solo miras el precio, llegas tarde.
- ❌ **Medir la montaña sin mirar el VIX.** Inventario grande con VIX en percentil 10
  = motor sin recorrido.
- ❌ **Extrapolar la mañana a la tarde.** El empuje se agota cuando el VIX se asienta;
  desde las 13:00 manda Charm.
- ❌ **Ignorar el calendario.** Leer el lunes post-OpEx con el mapa del jueves
  anterior: la montaña ya no está, el régimen cambió sin avisar.
- ❌ **Olvidar el lado call.** En persecuciones alcistas los dealers acumulan calls
  y el Vanna neto se da la vuelta. **El skew firma la dirección.**

## Del veredicto al trade
- **Post-evento con crush** → Bull Put Spread bajo el nuevo suelo, dentro de la
  ventana 30–90 min. Vendes con el dealer comprando a tu favor.
- **VIX cayendo, SPX plano** → sesgo alcista antes de que el precio lo muestre.
- **VIX subiendo, SPX plano** → no vendas puts aunque el precio parezca tranquilo;
  si el Gamma está cerca del flip, plantea coberturas.
- **Semana post-OpEx** → reduce tamaño: el viento de cola expiró con la montaña.
- **Cuadrante espiral** (Gamma neg + VIX subiendo + montaña grande) → no se vende
  prima. Sobrevivir también es estrategia.

> **El dashboard no te muestra Vanna: te muestra al dealer obligado.** Cuando el
> VIX se mueve y el SPX calla, ya sabes quién va a tener que comprar o vender antes
> de que el precio lo cuente.

---
**Fuentes:** Natenberg cap. 9 · SqueezeMetrics (vanna/charm en el hedging del MM) ·
Kolanovic/JPM (flujos sistemáticos) · Panel VS3D. Material educativo, no es
asesoramiento de inversión.
