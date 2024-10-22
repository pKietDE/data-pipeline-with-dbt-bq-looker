WITH Top_product AS(
    SELECT 
        dmp.product_id
        ,dmp.product_name
        ,dmp.current_url
        ,SUM(f.item_price * f.quantity) AS revenue
    FROM {{ref('dim_product')}} dmp 
    LEFT JOIN {{ref('fact_order')}} f 
    ON f.product_id = dmp.product_id
    WHERE dmp.product_name NOT IN ("link 404")
    GROUP BY dmp.product_id,dmp.product_name,dmp.current_url
), row_1 as (
    SELECT *
        ,ROW_NUMBER() OVER(PARTITION BY tp.product_id,tp.product_name,product_image,tp.revenue ) as rn
    FROM Top_product tp
    INNER JOIN {{ source("product_image","product_image")}} pi2
    ON tp.product_id = pi2.product_id
    ORDER BY tp.revenue DESC
)

select *
FROM row_1
where rn = 1




