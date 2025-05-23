#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# プログラム名 : example_script.py
# 概要         : 過去にランキング入りした商品コードを元に、楽天APIから商品情報を取得し、Supabaseに保存する
# 作成者       : Your Name
# 作成日       : 2025-05-19
# 更新履歴     :
#   - 2025-05-19 初版作成
#

import os
import requests
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time

# .env の読み込み（ローカル実行時のみ）
if os.path.exists('.env'):
    load_dotenv()

# --- ログ設定 ---
def setup_logger():
    is_github_actions = os.getenv('GIT_ACTIONS') == 'true'
    
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    handlers = [logging.StreamHandler()]  # 常に標準出力に出す

    if not is_github_actions:
        # ローカル環境ならログファイルにも出力
        log_dir = './logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'rakuten_products.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )

setup_logger()

# --- 環境変数 ---
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- 必須環境変数のチェック ---
if not all([RAKUTEN_APP_ID, SUPABASE_URL, SUPABASE_KEY]):
    raise EnvironmentError("必要な環境変数（RAKUTEN_APP_ID, SUPABASE_URL, SUPABASE_KEY）が不足しています")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAKUTEN_ITEM_SEARCH_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'

def fetch_item_by_code(item_code):
    params = {
        'applicationId': RAKUTEN_APP_ID,
        'format': 'json',
        'itemCode': item_code
    }
    try:
        response = requests.get(RAKUTEN_ITEM_SEARCH_URL, params=params)
        response.raise_for_status()
        result = response.json()
        logging.info(f"商品コード {item_code} の取得成功")
        return result.get('Items', [])
    except Exception as e:
        logging.exception(f"[ERROR] item_code={item_code} の取得失敗")
        return []

def fetch_tracked_item_codes():
    try:
        response = supabase.table('mst_rakuten_items').select('item_code').execute()
        codes = [row['item_code'] for row in response.data]
        logging.info(f"{len(codes)} 件の商品コードを取得")
        return codes
    except Exception as e:
        logging.exception("[ERROR] mst_rakuten_items の取得失敗")
        return []

def transform_items(items):
    transformed = []
    for wrapper in items:
        item = wrapper.get('Item', {})
        transformed.append({
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
            'affiliate_rate': str(item.get('affiliateRate', '0.0')),
            'availability': item.get('availability'),
            'credit_card_flag': bool(item.get('creditCardFlag')),
            'postage_flag': bool(item.get('postageFlag')),
            'tax_flag': bool(item.get('taxFlag')),
            'point_rate': item.get('pointRate'),
            'review_average': str(item.get('reviewAverage', '0.0')),
            'review_count': item.get('reviewCount'),
            'shop_code': item.get('shopCode'),
            'shop_name': item.get('shopName'),
            'shop_url': item.get('shopUrl'),
            'genre_id': item.get('genreId'),
            'medium_image_urls': json.dumps(item.get('mediumImageUrls', [])),
            'small_image_urls': json.dumps(item.get('smallImageUrls', [])),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
    logging.info(f"{len(transformed)} 件の商品データを変換完了")
    return transformed

def insert_into_supabase(data):
    if not data:
        logging.info("登録データが空のため、Supabaseへの登録をスキップ")
        return
    try:
        supabase.table('trn_rakuten_price_history_after_ranking').insert(data).execute()
        logging.info(f"{len(data)} 件のデータを Supabase の trn_rakuten_price_history_after_ranking に登録完了")
    except Exception as e:
        logging.exception("Supabase trn_rakuten_price_history_after_ranking 登録失敗")

def main():
    logging.info("=== スクリプト実行開始 ===")
    try:
        item_codes = fetch_tracked_item_codes()
        if not item_codes:
            logging.warning("追跡対象の商品コードが見つかりません")
            return

        all_items = []
        for code in item_codes:
            items = fetch_item_by_code(code)
            if items:
                transformed = transform_items(items)
                all_items.extend(transformed)
            time.sleep(1)  # 楽天APIの制限対策

        insert_into_supabase(all_items)
        logging.info("=== スクリプト実行完了 ===")
    except Exception as e:
        logging.exception("スクリプト全体で予期せぬエラーが発生しました")

if __name__ == '__main__':
    main()
