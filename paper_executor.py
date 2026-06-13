import threading
from datetime import datetime
from typing import Dict, List, Optional

class PaperExecutor:
    def __init__(self, initial_balance: float = 10000):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.ticket_counter = 1000
        self.lock = threading.Lock()

    def execute_order(self, symbol: str, action: str, price: float, lot: float = 0.01,
                      sl_pips: float = 50, tp_pips: float = 100) -> Optional[Dict]:
        with self.lock:
            spread = 0.5  # pips
            point = 0.0001
            if action.upper() == "BUY":
                entry = price + spread * point
                sl = entry - sl_pips * point
                tp = entry + tp_pips * point
            else:
                entry = price - spread * point
                sl = entry + sl_pips * point
                tp = entry - tp_pips * point
            ticket = self.ticket_counter
            self.ticket_counter += 1
            pos = {
                "ticket": ticket,
                "symbol": symbol,
                "action": action.upper(),
                "lot": lot,
                "entry_price": entry,
                "entry_time": datetime.now(),
                "sl_price": sl,
                "tp_price": tp,
                "sl_pips": sl_pips,
                "tp_pips": tp_pips
            }
            self.positions[symbol] = pos
            return pos

    def close_position(self, symbol: str, current_price: float) -> Optional[Dict]:
        with self.lock:
            pos = self.positions.pop(symbol, None)
            if not pos:
                return None
            if pos["action"] == "BUY":
                pnl = (current_price - pos["entry_price"]) * pos["lot"] * 100000
            else:
                pnl = (pos["entry_price"] - current_price) * pos["lot"] * 100000
            self.balance += pnl
            record = {**pos, "exit_price": current_price, "exit_time": datetime.now(),
                      "pnl": pnl, "balance_after": self.balance}
            self.trade_history.append(record)
            return record

    def update_positions(self, current_prices: Dict[str, float]):
        for sym, pos in list(self.positions.items()):
            price = current_prices.get(sym)
            if price:
                if pos["action"] == "BUY":
                    if price <= pos["sl_price"]:
                        self.close_position(sym, price)
                    elif price >= pos["tp_price"]:
                        self.close_position(sym, price)
                else:
                    if price >= pos["sl_price"]:
                        self.close_position(sym, price)
                    elif price <= pos["tp_price"]:
                        self.close_position(sym, price)

    def get_open_positions(self) -> List[Dict]:
        return list(self.positions.values())

    def get_balance(self) -> float:
        return self.balance

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        eq = self.balance
        for sym, pos in self.positions.items():
            price = current_prices.get(sym)
            if price:
                if pos["action"] == "BUY":
                    eq += (price - pos["entry_price"]) * pos["lot"] * 100000
                else:
                    eq += (pos["entry_price"] - price) * pos["lot"] * 100000
        return eq

    def close_all(self):
        for sym in list(self.positions.keys()):
            self.close_position(sym, 0)

    def get_summary(self) -> Dict:
        total_pnl = self.balance - self.initial_balance
        win_trades = [t for t in self.trade_history if t["pnl"] > 0]
        win_rate = len(win_trades) / len(self.trade_history) * 100 if self.trade_history else 0
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_pnl": total_pnl,
            "total_trades": len(self.trade_history),
            "win_trades": len(win_trades),
            "win_rate": win_rate
                        }
