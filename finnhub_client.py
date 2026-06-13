import requests
import pandas as pd
from utils import rate_limit
from config import FINNHUB_API_KEY

class FinnhubClient:
    def __init__(self):
        self.api_key = FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
        self.last_call = 0

    def _get(self, endpoint, params=None):
        self.last_call = rate_limit(self.last_call, 1.0)
        if params is None:
            params = {}
        params['token'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None

    def test_connection(self) -> bool:
        data = self._get("news", {"category": "forex", "minId": 0})
        return isinstance(data, list)

    def get_forex_quote(self, symbol: str):
        oanda = f"OANDA:{symbol}"
        data = self._get("quote", {"symbol": oanda})
        if data and "c" in data:
            return {"price": data["c"], "bid": data.get("b", data["c"]), "ask": data.get("a", data["c"])}
        return None

    def get_forex_candles(self, symbol: str, resolution: str = "60", count: int = 100):
        oanda = f"OANDA:{symbol}"
        now = int(pd.Timestamp.now().timestamp())
        if resolution == "D":
            from_ts = now - count * 86400
        else:
            from_ts = now - count * 3600
        data = self._get("forex/candle", {"symbol": oanda, "resolution": resolution,
                                          "from": from_ts, "to": now})
        if data and data.get("s") == "ok":
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(data["t"], unit="s"),
                "open": data["o"],
                "high": data["h"],
                "low": data["l"],
                "close": data["c"],
                "volume": data["v"]
            })
            return df
        return None

    def get_news(self, limit=5):
        data = self._get("news", {"category": "forex", "minId": 0})
        if data:
            return data[:limit]
        return []

    def get_sentiment(self, symbol: str):
        oanda = f"OANDA:{symbol}"
        return self._get("news-sentiment", {"symbol": oanda})
