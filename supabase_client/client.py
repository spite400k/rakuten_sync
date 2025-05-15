import os
from supabase_client import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_items(item):
    item_data = {
        "item_code": item["itemCode"],
        "item_name": item["itemName"],
        "item_caption": item["itemCaption"],
        "item_price": item["itemPrice"],
        "shop_name": item["shopName"],
    }

    supabase.table("mst_item_detail").upsert(item_data).execute()

    for size, field in [("small", "smallImageUrls"), ("medium", "mediumImageUrls")]:
        for image in item.get(field, []):
            supabase.table("mst_item_detail_image").insert({
                "item_code": item["itemCode"],
                "size": size,
                "image_url": image["imageUrl"]
            }).execute()

    for tag_id in item.get("tagIds", []):
        supabase.table("mst_item_detail_tag").insert({
            "item_code": item["itemCode"],
            "tag_id": tag_id
        }).execute()
