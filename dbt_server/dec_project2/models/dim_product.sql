-- models/dim_product.sql
{{ config(materialized='table') }}

SELECT DISTINCT
  _id as product_id
  ,{{ handle_null("product_name", "Not found") }} as product_name
  ,{{ handle_null("current_url", "Not found") }} as current_url
  ,{{ handle_null("alloy", "none") }} as alloy
  ,{{ handle_null("stone", "none") }} as stone
  ,view_click
FROM {{ source('product_infor', 'product_infor') }}