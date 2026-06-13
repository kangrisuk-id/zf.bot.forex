import time
from datetime import datetime

def rate_limit(last_called: float, min_interval: float = 1.0) -> float:
    """Jeda untuk rate limiting API."""
    now = time.time()
    elapsed = now - last_called
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    return time.time()

def timestamp_to_str(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def save_json(data: dict, filename: str):
    import json
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def load_json(filename: str) -> dict:
    import json
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {}
