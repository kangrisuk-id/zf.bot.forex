import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)

    def send_message(self, text: str):
        if not self.enabled:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Telegram error: {e}")

    def send_trade_signal(self, symbol, action, confidence, reason, price):
        msg = f"🔔 <b>ZF Signal</b>\n{symbol}\n<b>{action}</b> | conf: {confidence}%\nPrice: {price:.5f}\nReason: {reason}"
        self.send_message(msg)

    def send_execution(self, symbol, action, lot, price, sl, tp):
        msg = f"✅ <b>ORDER EXECUTED</b>\n{symbol} {action} {lot} lot\nEntry: {price:.5f}\nSL: {sl:.5f} | TP: {tp:.5f}"
        self.send_message(msg)

    def send_daily_summary(self, balance, equity, trades_today, pnl_today):
        msg = f"📊 <b>Daily Summary</b>\nBalance: {balance:.2f}\nEquity: {equity:.2f}\nTrades: {trades_today}\nPnL: {pnl_today:.2f}"
        self.send_message(msg)

    def send_optimization_result(self, best_params, winrate):
        msg = f"🧠 <b>Optimization Result</b>\nWinrate: {winrate:.2f}%\nParams: {best_params}"
        self.send_message(msg)
