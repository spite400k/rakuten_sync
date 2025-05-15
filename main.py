from rakuten.api import fetch_ranking_items, fetch_item_details
from supabase_client.client import insert_items
from utils.logger import logger

def main():
    logger.info("楽天ランキング取得開始")

    ranking_items = fetch_ranking_items()
    logger.info(f"ランキング取得: {len(ranking_items)}件")

    for item in ranking_items:
        item_code = item.get("itemCode")
        if not item_code:
            continue

        details = fetch_item_details(item_code)
        if details:
            insert_items(details)

    logger.info("処理完了")

if __name__ == "__main__":
    main()
