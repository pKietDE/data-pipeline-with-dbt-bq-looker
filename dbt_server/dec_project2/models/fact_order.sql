{{ config(materialized='table') }}

WITH checkout_success AS (
    SELECT  * 
    FROM {{ source('glamira_raw', 'glamira_raw') }}
    WHERE collection = 'checkout_success'
),
unnested_cart_products AS (
    SELECT
        *
        ,cart_product
    FROM checkout_success,
    UNNEST(cart_products) AS cart_product
), glamira_transform as(
    SELECT
        {{ dbt_utils.generate_surrogate_key(['order_id', 'cart_product.product_id']) }} AS order_item_key
        ,order_id
        ,CAST(cart_product.product_id as INT64) as product_id
        ,{{ handle_null("user_id_db", "None") }} AS user_id_db
        ,TIMESTAMP_SECONDS(time_stamp) AS order_date  
        ,ip
        ,user_agent
        ,resolution
        ,device_id
        ,api_version
        ,store_id
        ,CAST(local_time AS TIMESTAMP) AS local_time
        ,show_recommendation
        ,current_url
        ,{{ handle_null("referrer_url", "None") }} AS referrer_url
        ,{{ handle_null("email_address", "None") }} AS email_address
        ,cart_product.price AS item_price
        ,COALESCE(NULLIF(TRIM(cart_product.currency), ""), "None") AS currency
        ,cart_product.amount AS quantity
        ,{{ handle_null("cart_product.options[SAFE_OFFSET(0)].option_label", "None")}} AS option_label
        ,{{ handle_null("cart_product.options[SAFE_OFFSET(0)].value_label", "None")}} AS value_label
        ,{{ handle_null("cart_product.options[SAFE_OFFSET(0)].value_id", "None")}} AS value_id
        ,ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY time_stamp ) as rn
    FROM unnested_cart_products
)

--item_price = 0 => item do bi loi 
SELECT *
FROM glamira_transform
where item_price > 0 






