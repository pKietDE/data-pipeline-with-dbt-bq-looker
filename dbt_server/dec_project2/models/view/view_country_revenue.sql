SELECT 
    dmdl.country_long as country
    ,SUM(fo.item_price * fo.quantity) as revenue
FROM {{ ref("fact_order") }} fo
INNER JOIN {{ ref("dim_ip_location") }} dmdl
    ON fo.ip = dmdl.ip
GROUP BY country