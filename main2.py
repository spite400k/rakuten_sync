import requests
from supabase import create_client
from datetime import datetime
import os
from pprint import pprint

# 環境変数または設定ファイルから取得する方式でも可
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAKUTEN_API_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601'

def fetch_ranking_items():
    params = {
        'applicationId': RAKUTEN_APP_ID,
        'format': 'json',
        'hits': 100
    }
    response = requests.get(RAKUTEN_API_URL, params=params)
    response.raise_for_status()
    return response.json().get('Items', [])

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
            'medium_image_urls': item.get('mediumImageUrls'),
            'small_image_urls': item.get('smallImageUrls'),
            'timestamp': datetime.utcnow().isoformat()
        })
    return transformed

def insert_into_supabase(data):
    try:
        supabase.table('trn_rakuten_ranking').upsert(data).execute()
    except Exception as e:
        pprint(f"Supabase trn_rakuten_ranking upsert失敗: {str(e)}")

def main():
    items = fetch_ranking_items()
    if not items:
        print("データが取得できませんでした")
        return
    transformed_data = transform_items(items)
    insert_into_supabase(transformed_data)

if __name__ == '__main__':
    main()
