import requests
from supabase import create_client
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

import logging
import json
import platform


# --- 環境変数の取得 ---
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not RAKUTEN_APP_ID or not SUPABASE_URL or not SUPABASE_KEY:
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAKUTEN_API_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601'

def fetch_ranking_items():
    params = {
        'applicationId': RAKUTEN_APP_ID,
        'format': 'json',
        'hits': 100
    }
    try:
        response = requests.get(RAKUTEN_API_URL, params=params)
        response.raise_for_status()
        return response.json().get('Items', [])
    except Exception as e:
        return []

def transform_items(items):
    transformed = []
    for wrapper in items:
        item = wrapper.get('Item', {})
        transformed.append({
            'rank': item.get('rank'),
            'item_code': item.get('itemCode'),
            'item_name': item.get('itemName'),
            'item_caption': item.get('itemCaption'),
            'catchcopy': item.get('catchcopy'),
            'item_price': int(item.get('itemPrice', 0)),
            'item_price_base_field': item.get('itemPriceBaseField'),
            'item_price_min1': int(item.get('itemPriceMin1', 0)),
            'item_price_min2': int(item.get('itemPriceMin2', 0)),
            'item_price_min3': int(item.get('itemPriceMin3', 0)),
            'item_price_max1': int(item.get('itemPriceMax1', 0)),
            'item_price_max2': int(item.get('itemPriceMax2', 0)),
            'item_price_max3': int(item.get('itemPriceMax3', 0)),
            'item_url': item.get('itemUrl'),
            'affiliate_url': item.get('affiliateUrl'),
            'affiliate_rate': float(item.get('affiliateRate', 0.0)),
            'availability': item.get('availability'),
            'credit_card_flag': bool(item.get('creditCardFlag')),
            'postage_flag': bool(item.get('postageFlag')),
            'tax_flag': bool(item.get('taxFlag')),
            'point_rate': item.get('pointRate'),
            'review_average': float(item.get('reviewAverage', 0.0)),
            'review_count': item.get('reviewCount'),
            'shop_code': item.get('shopCode'),
            'shop_name': item.get('shopName'),
            'shop_url': item.get('shopUrl'),
            'genre_id': item.get('genreId'),
            'medium_image_urls': json.dumps(item.get('mediumImageUrls')),
            'small_image_urls': json.dumps(item.get('smallImageUrls')),
            'timestamp': datetime.now().isoformat(),
        })
    return transformed

def insert_into_supabase(data):
    if not data:
        return
    try:
        supabase.table('trn_rakuten_ranking').upsert(data).execute()
    except Exception as e:
        return
    
def main():
    items = fetch_ranking_items()
    if not items:
        return
    transformed_data = transform_items(items)
    insert_into_supabase(transformed_data)

if __name__ == '__main__':
    main()
