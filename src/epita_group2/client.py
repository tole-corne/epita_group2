import requests
from epita_group2.config import config

URL = "https://ipinfo.io/json"

def fetch_live_data() -> dict:
    config.validate()
    headers = {"Authorization": f"Bearer {config.api_key}"}
    resp = requests.get(URL, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        "status": "LIVE_SUCCESS",
        "ip": data.get("ip"),
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country"),
        "org": data.get("org"),
    }
