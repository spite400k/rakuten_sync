#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# プログラム名 : example_script.py
# 概要         : 楽天APIを利用してランキング情報を取得し、Supabaseに保存する
# 作成者       : Your Name
# 作成日       : 2025-05-19
# 更新履歴     :
#   - 2025-05-19 初版作成
#

import requests
from supabase import create_client
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

import logging
import json
import platform

# --- .env の読み込み（ローカルのみ） ---
if os.getenv("ENV") != "production":
    load_dotenv()

# --- ログ設定 ---
def setup_logger():
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
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

# --- 環境変数の取得 ---
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not RAKUTEN_APP_ID or not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("必要な環境変数が設定されていません")
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
        logging.info("楽天ランキングデータの取得に成功")
        return response.json().get('Items', [])
    except Exception as e:
        logging.error(f"楽天ランキング取得失敗: {str(e)}")
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
    logging.info(f"{len(transformed)} 件のランキングデータを整形")
    return transformed

def insert_into_supabase(data):
    if not data:
        logging.warning("Supabaseへの挿入対象データが空です")
        return
    try:
        supabase.table('trn_rakuten_ranking').upsert(data).execute()
        logging.info(f"{len(data)} 件のデータを trn_rakuten_ranking に保存完了")
    except Exception as e:
        logging.error(f"Supabase trn_rakuten_ranking upsert失敗: {str(e)}")

def main():
    logging.info("=== 楽天ランキング同期バッチ 開始 ===")
    items = fetch_ranking_items()
    if not items:
        logging.warning("ランキングデータが取得できませんでした")
        return
    transformed_data = transform_items(items)
    insert_into_supabase(transformed_data)
    logging.info("=== 楽天ランキング同期バッチ 終了 ===")

if __name__ == '__main__':
    main()
