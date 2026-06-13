import numpy as np
import pandas as pd
from config import ADX_THRESHOLD, REGIME_LOOKBACK

class MarketRegimeDetector:
    def __init__(self):
        self.lookback = REGIME_LOOKBACK
        self.adx_threshold = ADX_THRESHOLD

    def detect_regime(self, close_prices: pd.Series):
        if len(close_prices) < self.lookback:
            return {"regime": "UNKNOWN", "trend_slope": 0, "volatility": 0,
                    "is_sideways": False, "is_high_vol": False}
        x = np.arange(self.lookback)
        y = close_prices.iloc[-self.lookback:].values
        slope = np.polyfit(x, y, 1)[0]
        trend = slope / close_prices.iloc[-1] * 100
        returns = close_prices.pct_change().dropna()
        vol = returns.std() * 100
        adx_est = min(100, abs(trend) * 10)
        is_sideways = adx_est < self.adx_threshold
        is_high_vol = vol > (returns.std() * 2)
        if is_high_vol:
            regime = "HIGH_VOLATILITY"
        elif is_sideways:
            regime = "SIDEWAYS"
        else:
            if trend > 0.1:
                regime = "STRONG_UPTREND" if trend > 0.3 else "WEAK_UPTREND"
            elif trend < -0.1:
                regime = "STRONG_DOWNTREND" if trend < -0.3 else "WEAK_DOWNTREND"
            else:
                regime = "SIDEWAYS"
        return {"regime": regime, "trend_slope": trend, "volatility": vol,
                "is_sideways": is_sideways, "is_high_vol": is_high_vol}
