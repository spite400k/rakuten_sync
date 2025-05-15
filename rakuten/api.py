import httpx
import os
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("RAKUTEN_APP_ID")

def fetch_ranking_items():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628"
    params = {
        "applicationId": APP_ID,
        "format": "json"
    }
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return [item["Item"] for item in response.json().get("Items", [])]

def fetch_item_details(item_code: str):
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    params = {
        "applicationId": APP_ID,
        "format": "json",
        "itemCode": item_code
    }
    response = httpx.get(url, params=params)
    response.raise_for_status()
    items = response.json().get("Items", [])
    return items[0]["Item"] if items else None
