{{ config(materialized='table') }}

WITH REPLACE_TABLE AS (
    SELECT 
        ip
        ,REPLACE(country_short,'-','Not Found') AS country_short
        ,REPLACE(country_long,'-','Not Found') AS country_long
        ,REPLACE(region,'-','Not Found') AS region
        ,REPLACE(city,'-','Not Found') AS city
        ,CASE WHEN longtitude = 0 THEN 0.0 ELSE longtitude END AS longtitude
        ,CASE WHEN latitude = 0 THEN 0.0 ELSE latitude END AS latitude
        ,REPLACE(zip_code,'-','Not Found') AS zip_code
        ,REPLACE(timezone,'-','Not Found') AS timezone 
    FROM {{ source('ip_locations','ip_locations') }}

)

SELECT *
FROM REPLACE_TABLE

