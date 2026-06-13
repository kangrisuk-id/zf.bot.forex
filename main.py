import time
import schedule
from datetime import datetime
from config import FOREX_PAIRS, INITIAL_BALANCE, LOT_SIZE, MAX_POSITIONS, INTERVAL_MINUTES
from data_manager import DataManager
from paper_executor import PaperExecutor
from zf_core import ZFCore
from market_regime import MarketRegimeDetector
from trading_style import TradingStyleSelector
from ai_interface import AIInterface
from telegram_bot import TelegramBot
from backtest_optimizer import BacktestOptimizer
from utils import load_json

class ZFRobot:
    def __init__(self):
        self.data = DataManager()
        self.executor = PaperExecutor(INITIAL_BALANCE)
        self.zf = ZFCore()
        self.regime = MarketRegimeDetector()
        self.style = TradingStyleSelector()
        self.ai = AIInterface()
        self.tg = TelegramBot()
        self.symbols = FOREX_PAIRS
        self.best_params = load_json('best_params.json').get('best_params', {})

    def process_symbol(self, symbol):
        hist = self.data.get_historical_data(symbol, lookback_days=50)
        if hist is None or len(hist) < 50:
            return None
        metrics = self.zf.compute_metrics(hist)
        if not metrics:
            return None
        regime_info = self.regime.detect_regime(hist['close'])
        style, style_params = self.style.select_style(
            metrics['Decay_10d (%)'], metrics['ZF-Score'],
            regime_info['volatility'], regime_info
        )
        context = self.data.get_live_context(symbol)
        ai_decision = self.ai.analyze(symbol, metrics, context)
        price = context['quote'].get('price') if context['quote'] else None
        return {
            'symbol': symbol,
            'metrics': metrics,
            'regime': regime_info,
            'style': style,
            'style_params': style_params,
            'decision': ai_decision,
            'price': price
        }

    def run_cycle(self):
        print(f"\n=== Cycle at {datetime.now()} ===")
        # Update harga semua simbol
        prices = {}
        for sym in self.symbols:
            p = self.data.get_current_price(sym)
            if p:
                prices[sym] = p
        self.executor.update_positions(prices)
        # Proses sinyal
        open_syms = [p['symbol'] for p in self.executor.get_open_positions()]
        for sym in self.symbols:
            res = self.process_symbol(sym)
            if not res or res['decision']['action'] not in ['BUY','SELL']:
                continue
            conf = res['decision']['confidence']
            if conf < 60:
                continue
            if sym in open_syms:
                continue
            if len(self.executor.get_open_positions()) >= MAX_POSITIONS:
                continue
            price = res['price']
            if not price:
                continue
            lot = LOT_SIZE * res['style_params'].get('lot_multiplier', 1.0) * (conf/100)
            sl = res['style_params'].get('stop_loss_pips', 50)
            tp = res['style_params'].get('target_profit_pips', 100)
            self.executor.execute_order(sym, res['decision']['action'], price, lot, sl, tp)
            self.tg.send_execution(sym, res['decision']['action'], lot, price, sl, tp)
            self.tg.send_trade_signal(sym, res['decision']['action'], conf, res['decision']['reason'], price)
        equity = self.executor.get_equity(prices)
        print(f"Balance: {self.executor.get_balance():.2f} | Equity: {equity:.2f}")

    def run_forever(self):
        self.tg.send_message("🤖 ZF-Core Robot started")
        schedule.every(INTERVAL_MINUTES).minutes.do(self.run_cycle)
        # Jadwalkan optimasi mingguan
        schedule.every().sunday.at("00:00").do(self.run_weekly_optimization)
        self.run_cycle()
        while True:
            schedule.run_pending()
            time.sleep(10)

    def run_weekly_optimization(self):
        self.tg.send_message("🔄 Memulai optimasi mingguan...")
        opt = BacktestOptimizer()
        result = opt.weekly_optimization()
        self.best_params = result['best_params']
        self.tg.send_optimization_result(self.best_params, result['best_winrate'])

if __name__ == "__main__":
    # Cek API key
    from finnhub_client import FinnhubClient
    f = FinnhubClient()
    if not f.test_connection():
        print("Finnhub API key invalid")
        exit(1)
    ai = AIInterface()
    if not ai.test_connection():
        print("Gemini API key invalid")
        exit(1)
    robot = ZFRobot()
    robot.run_forever()
