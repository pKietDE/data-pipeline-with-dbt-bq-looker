{{ config(materialized='table') }}
WITH extracted_data AS (
  SELECT 
    JSON_EXTRACT_SCALAR(TO_JSON_STRING(t), '$.product_id') as product_id,
    JSON_EXTRACT_SCALAR(TO_JSON_STRING(t), '$.product_name') as product_name,
    JSON_EXTRACT_SCALAR(TO_JSON_STRING(t), '$.product_link') as product_link,
    JSON_EXTRACT_SCALAR(TO_JSON_STRING(t), '$.product_image') as product_image,
    JSON_EXTRACT_SCALAR(TO_JSON_STRING(t), '$.product_current_url') as product_current_url
  FROM {{ source('product_image', 'product_image') }} t
)
SELECT
  CAST(COALESCE(product_id, '0') AS INT64) AS product_id,
  COALESCE(product_name, 'Not Found') AS product_name,
  COALESCE(product_link, 'Not Found') AS product_link,
  COALESCE(product_image, 'Not Found') AS product_image,
  COALESCE(product_current_url, 'Not Found') AS product_current_url
FROM extracted_data