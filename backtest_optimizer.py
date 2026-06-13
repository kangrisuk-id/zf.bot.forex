import itertools
from datetime import datetime, timedelta
from typing import Dict
from data_manager import DataManager
from paper_executor import PaperExecutor
from zf_core import ZFCore
from config import FOREX_PAIRS, LOT_SIZE, BACKTEST_DAYS
from utils import save_json

class BacktestOptimizer:
    def __init__(self):
        self.data_mgr = DataManager()
        self.zf = ZFCore()
        self.symbols = FOREX_PAIRS

    def run_backtest(self, start_date: datetime, end_date: datetime, params: Dict) -> Dict:
        executor = PaperExecutor(initial_balance=10000)
        current = start_date
        step_hours = 6
        while current <= end_date:
            prices = {}
            for sym in self.symbols:
                price = self._get_price_at(sym, current)
                if price:
                    prices[sym] = price
            executor.update_positions(prices)
            for sym in self.symbols:
                hist = self.data_mgr.get_historical_data(sym, lookback_days=params['lookback'], end_time=current)
                if hist is None or len(hist) < params['lookback']:
                    continue
                metrics = self.zf.compute_metrics(hist)
                if not metrics:
                    continue
                if abs(metrics['Decay_10d (%)']) < params['decay_thresh']:
                    continue
                if metrics['ZF-Score'] < params['zf_thresh']:
                    continue
                action = 'BUY' if metrics['Decay_10d (%)'] > 0 else 'SELL'
                price = prices.get(sym)
                if price and sym not in executor.positions:
                    executor.execute_order(sym, action, price, lot=LOT_SIZE,
                                           sl_pips=params['sl'], tp_pips=params['tp'])
            current += timedelta(hours=step_hours)
        executor.close_all()
        return executor.get_summary()

    def _get_price_at(self, symbol, dt: datetime):
        hist = self.data_mgr.get_historical_data(symbol, lookback_days=100, end_time=dt)
        if hist is not None and not hist.empty:
            return hist.iloc[-1]['close']
        return None

    def grid_search(self, start_date: datetime, end_date: datetime) -> Dict:
        param_grid = {
            'zf_thresh': [0.2, 0.3, 0.4, 0.5],
            'decay_thresh': [0.3, 0.5, 0.8, 1.0],
            'sl': [20, 30, 50],
            'tp': [40, 60, 100],
            'lookback': [30, 40, 50]
        }
        keys = list(param_grid.keys())
        best_winrate = 0
        best_params = None
        for values in itertools.product(*param_grid.values()):
            params = dict(zip(keys, values))
            summary = self.run_backtest(start_date, end_date, params)
            win = summary['win_rate']
            if win > best_winrate:
                best_winrate = win
                best_params = params
                print(f"New best: {win:.2f}% with {params}")
        result = {'best_params': best_params, 'best_winrate': best_winrate, 'best_summary': summary}
        save_json(result, 'best_params.json')
        return result

    def weekly_optimization(self):
        end = datetime.now()
        start = end - timedelta(days=BACKTEST_DAYS)
        return self.grid_search(start, end)
