import google.generativeai as genai
import json
from config import GEMINI_API_KEY

class AIInterface:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def test_connection(self):
        try:
            resp = self.model.generate_content("Say API OK")
            return "OK" in resp.text
        except:
            return False

    def analyze(self, symbol: str, zf_metrics: dict, finnhub_data: dict) -> dict:
        prompt = f"""
Anda Arsitek ZF-Core. Analisis {symbol}.
ZF Metrics: {zf_metrics}
Finnhub: quote={finnhub_data.get('quote')}, sentiment={finnhub_data.get('sentiment')}, news={finnhub_data.get('news_headlines')}
Output JSON: {{"action": "BUY/SELL/HOLD", "confidence": 0-100, "reason": "..."}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1:
                return json.loads(text[start:end])
        except:
            pass
        return {"action": "HOLD", "confidence": 50, "reason": "AI error"}
