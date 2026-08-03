# 🔬 Corroboración: MarketSnack (MS) vs tus Clases

> Cruce del [Playbook de MarketSnack](Playbook%20MarketSnack.md) contra tus notas de clase
> (Gamma/Charm/MM 0DTE, Iron Butterfly, Vanna, VS3D). Hecho 2026-08-01, "con calma".
> **Conclusión corta: MS CONFIRMA tus clases en gamma, pero tus clases van MÁS ALLÁ, y hay
> una jerarquía de fuentes que respetar.**

## 1. ✅ Dónde MS CONFIRMA tus clases (misma verdad)

- **"No analizamos dirección, analizamos comportamiento."** — idéntico en ambos.
- **Gamma+ contiene (rango) · Gamma− acelera (volátil).** MS lo dice igual que tu clase de
  Gamma/Charm/MM. El signo **NO** es alcista/bajista.
- **Tu Iron Butterfly se apoya en las mismas piezas que calcula MS:**
  - **Centro de la mariposa = el IMÁN** (donde el mercado gravita). MS calcula el magnet.
  - **Alas = fuera del straddle del día.** MS muestra el straddle.
  - **Se usa en rango = gamma+.** MS: gamma+ = range-bound = terreno de la mariposa.
  - **Gamma− cerca del vto = 0DTE peligroso.** MS: el gamma flip te avisa cuándo.
  → **MarketSnack básicamente operacionaliza tu método de mariposa.**

## 2. 🔼 Dónde tus CLASES van MÁS ALLÁ de MS (MS NO lo tiene)

- **Vanna** (∂Δ/∂σ): la **vol** mueve el delta sin que el precio se mueva → el "rally sin
  compradores", VIX↓/SPX-plano = motor alcista cargando, VIX↑/SPX-plano = venta mecánica.
  **MS no mide Vanna.**
- **Charm** (el reloj, presión hacia ~1 PM). MS lo menciona apenas; tu clase lo usa a fondo.
- **Straddle / Spot vs Straddle**: "el movimiento tiene que ganarle al tiempo." MS muestra el
  straddle pero no enseña esta lectura.
- **Gamma NEUTRAL como régimen aparte** ("basta con neutral para cambiar de carácter"). MS solo
  habla de +/−.

## 3. ⚠️ LA PIEZA MÁS IMPORTANTE — jerarquía de fuentes (dato real vs estimación)

Tu clase de **VS3D** lo dice explícito: *"la mayoría de las herramientas de gamma **ESTIMAN** la
posición del dealer desde el interés abierto + suposiciones (el método bid/ask que **falla**)."*

- **VS3D usa datos REALES de clearing de OCC/CBOE, por participante** → **VE** la posición del MM,
  no la estima. Filtra el volumen MM-contra-MM.
- **MarketSnack ESTIMA** el GEX desde OI + gamma (como SpotGamma/MenthorQ). Es el método que tu
  clase dice que **falla**.
- **Mi `gex.py` también ESTIMA** (mismo método: gamma × OI). → También es estimación, no dato real.

> 🎯 **Regla de oro:** cuando **VS3D y MarketSnack (o mi gex.py) difieran → CREE A VS3D.**
> VS3D = la verdad de la posición del dealer. MS/gex.py = estimación rápida de apoyo.
> **Tu instinto de compartir SIEMPRE el VS3D es correcto según tu propia clase.**

## 4. 🧩 Qué aporta cada fuente (síntesis)

| Fuente | Qué es | Peso |
|---|---|---|
| **VS3D** (tú compartes) | Posición REAL del MM por strike/vto (clearing) | **Máximo** — la autoridad |
| **MarketSnack** (Claude jala) | GEX estimado + magnet/walls/flip + **Flow Tape institucional** | Apoyo; el Flow Tape SÍ es único |
| **Mi `gex.py`** (Claude calcula) | GEX estimado desde Schwab | Respaldo cuando no hay VS3D/MS |
| **Tus clases** | El marco completo: Vanna + Charm + Straddle + Iron Butterfly + régimen | El **método**; todo lo demás son lentes |

**Lo único que MS te da y las otras no enfatizan:** el **Institutional Flow Tape** (dónde se
posiciona el dinero grande, filtrado por algoritmo). Eso sí súmalo — no lo tienes en VS3D ni en clase.

## 5. Regla operativa reconciliada (para tus mariposas)

1. **Régimen primero** con VS3D (verde=contiene / rojo=acelera) — la fuente real. MS/gex.py confirman.
2. **Centro** de la mariposa en el **imán**; **alas** fuera del **straddle**.
3. Solo en **gamma+ (pin)**; en gamma− o cerca del flip, **espera el crush** (0DTE castiga).
4. Vigila **Vanna** (VIX y SPX juntos) y **Charm** (el reloj ~1 PM) — eso NO está en MS.
5. El **Flow Tape de MS** para ver dónde apuesta el dinero (vender puts=alcista, etc.).
6. Gatillo core intacto: **volumen probando + confluencia**. Ver [[regla-volumen-obligatorio]],
   [[sistemas-separados-0dte-vs-confluencia]], [[verificacion-automatica-siempre]].
