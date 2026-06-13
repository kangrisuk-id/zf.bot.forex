import pandas as pd
from finnhub_client import FinnhubClient

class DataManager:
    def __init__(self):
        self.finnhub = FinnhubClient()
        self.cache = {}

    def get_historical_data(self, symbol: str, lookback_days: int = 50, end_time=None):
        # end_time ignored for simplicity
        if symbol in self.cache:
            df = self.cache[symbol]
            if len(df) >= lookback_days:
                return df.tail(lookback_days)
        df = self.finnhub.get_forex_candles(symbol, resolution="60", count=lookback_days + 20)
        if df is not None and not df.empty:
            self.cache[symbol] = df
            return df.tail(lookback_days)
        return None

    def get_current_price(self, symbol: str):
        quote = self.finnhub.get_forex_quote(symbol)
        if quote:
            return quote.get("price")
        return None

    def get_live_context(self, symbol: str):
        quote = self.finnhub.get_forex_quote(symbol)
        news = self.finnhub.get_news(limit=5)
        sentiment = self.finnhub.get_sentiment(symbol)
        headlines = [n.get("headline", "") for n in news]
        return {"quote": quote, "sentiment": sentiment, "news_headlines": headlines}
