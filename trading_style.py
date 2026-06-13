class TradingStyleSelector:
    def select_style(self, decay_pct, zf_score, volatility, regime_info):
        abs_decay = abs(decay_pct)
        regime = regime_info.get("regime", "UNKNOWN")
        is_high_vol = regime_info.get("is_high_vol", False)
        is_sideways = regime_info.get("is_sideways", False)

        if is_high_vol:
            return "NO_TRADE", {"reason": "High volatility", "lot_multiplier": 0}
        if abs_decay < 0.5 and zf_score < 0.3 and volatility < 0.5 and is_sideways:
            return "SCALPING", {"max_hold_minutes": 30, "target_profit_pips": 5,
                                "stop_loss_pips": 10, "lot_multiplier": 0.5}
        elif 0.5 <= abs_decay < 2.0 and zf_score < 0.6:
            return "DAY_TRADING", {"max_hold_hours": 8, "target_profit_pips": 20,
                                   "stop_loss_pips": 15, "lot_multiplier": 1.0}
        elif 2.0 <= abs_decay < 5.0 and zf_score < 0.7:
            return "SWING", {"max_hold_days": 5, "target_profit_pips": 50,
                             "stop_loss_pips": 30, "lot_multiplier": 1.2}
        elif abs_decay >= 5.0 and zf_score > 0.5 and regime in ["STRONG_UPTREND", "STRONG_DOWNTREND"]:
            return "LONG_POSITION", {"max_hold_weeks": 4, "target_profit_pips": 200,
                                     "stop_loss_pips": 80, "lot_multiplier": 1.5}
        else:
            return "NO_TRADE", {"reason": "No clear signal", "lot_multiplier": 0}
