# ============================================================================
# BACKTEST E3 — Descuento bajo EMA200 (estrategia de Tania) para QuantConnect
# ----------------------------------------------------------------------------
# Prueba tu idea: comprar calidad cuando está BAJO su EMA de 200 días,
# y salir en +25%. Empieza con poco ($10,000) y máximo 10% por posición.
#
# CÓMO USARLO:
#   1. En quantconnect.com: Create New Algorithm (Python)
#   2. Borra el código de ejemplo y pega TODO esto
#   3. Botón "Backtest" (arriba a la derecha)
#   4. Cuando termine, compárteme los resultados (o captura del reporte)
#
# Esto es SOLO research — probar si la idea tiene edge en el pasado.
# El pasado no garantiza el futuro; sirve para descartar ideas malas.
# ============================================================================
from AlgorithmImports import *


class EMA200DiscountTania(QCAlgorithm):

    def Initialize(self):
        # --- periodo y capital (empezar con poco, como tu plan) ---
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2026, 7, 1)
        self.SetCash(10000)

        # --- tu watchlist de CALIDAD (ajústala a las que te interesen) ---
        tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "V", "MA",
                   "COST", "UNH", "HD", "PG"]

        self.datos = {}
        for t in tickers:
            eq = self.AddEquity(t, Resolution.Daily)
            # EMA de 200 días por cada acción
            self.datos[eq.Symbol] = self.EMA(eq.Symbol, 200, Resolution.Daily)

        # --- tus reglas ---
        self.take_profit = 0.25   # salir en +25% (tu objetivo)
        self.max_pct = 0.10       # <= 10% del capital por posición (tu límite)

        # calentar la EMA (necesita 200 días antes de operar)
        self.SetWarmUp(200, Resolution.Daily)

    def OnData(self, data):
        if self.IsWarmingUp:
            return

        for symbol, ema in self.datos.items():
            if not ema.IsReady or symbol not in data.Bars:
                continue

            precio = data.Bars[symbol].Close
            posicion = self.Portfolio[symbol]

            if not posicion.Invested:
                # ENTRAR: el precio está BAJO su EMA200 (descuento técnico)
                if precio < ema.Current.Value:
                    self.SetHoldings(symbol, self.max_pct)
                    self.Debug(f"COMPRA {symbol.Value} @ {precio:.2f} "
                               f"(EMA200 {ema.Current.Value:.2f})")
            else:
                # SALIR: +25% de apreciación
                if posicion.UnrealizedProfitPercent >= self.take_profit:
                    self.Liquidate(symbol)
                    self.Debug(f"VENTA +25% {symbol.Value} @ {precio:.2f}")
