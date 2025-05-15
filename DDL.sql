-- mst_item_detail（商品詳細マスタ）
create table if not exists mst_item_detail (
  item_code text primary key,
  item_name text,
  item_caption text,
  catchcopy text,
  item_price integer,
  item_price_min1 integer,
  item_price_min2 integer,
  item_price_min3 integer,
  item_price_max1 integer,
  item_price_max2 integer,
  item_price_max3 integer,
  item_url text,
  shop_code text,
  shop_name text,
  shop_url text,
  affiliate_rate numeric,
  affiliate_url text,
  credit_card_flag boolean,
  postage_flag boolean,
  availability integer,
  genre_id text,
  review_average numeric,
  review_count integer,
  point_rate integer,
  point_rate_start_time timestamp,
  point_rate_end_time timestamp,
  start_time timestamp,
  end_time timestamp,
  tax_flag boolean,
  gift_flag boolean,
  image_flag boolean,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

-- mst_item_detail_image（商品画像）
create table if not exists mst_item_detail_image (
  id uuid primary key default gen_random_uuid(),
  item_code text references mst_item_detail(item_code) on delete cascade,
  size text, -- 'small' または 'medium'
  image_url text
);


-- mst_item_detail_tag（商品タグ）
create table if not exists mst_item_detail_tag (
  id uuid primary key default gen_random_uuid(),
  item_code text references mst_item_detail(item_code) on delete cascade,
  tag_id bigint
);


CREATE TABLE trn_rakuten_ranking (
    id SERIAL PRIMARY KEY,
    rank INTEGER,
    item_code TEXT,
    item_name TEXT,
    item_caption TEXT,
    catchcopy TEXT,
    item_price INTEGER,
    item_price_base_field TEXT,
    item_price_min1 INTEGER,
    item_price_min2 INTEGER,
    item_price_min3 INTEGER,
    item_price_max1 INTEGER,
    item_price_max2 INTEGER,
    item_price_max3 INTEGER,
    item_url TEXT,
    affiliate_url TEXT,
    affiliate_rate NUMERIC(5,2),
    availability INTEGER,
    credit_card_flag BOOLEAN,
    postage_flag BOOLEAN,
    tax_flag BOOLEAN,
    point_rate INTEGER,
    review_average NUMERIC(3,1),
    review_count INTEGER,
    shop_code TEXT,
    shop_name TEXT,
    shop_url TEXT,
    genre_id TEXT,
    medium_image_urls JSONB,
    small_image_urls JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);