SELECT 
    EXTRACT(YEAR FROM fo.order_date) AS sales_year
    ,EXTRACT(QUARTER FROM fo.order_date) AS sales_quarter
    ,SUM(item_price * quantity) AS total_sales
FROM 
    {{ ref("fact_order")}} fo

INNER JOIN 
    {{ ref("dim_date")}} dmd
ON
    fo.order_date = dmd.time_stamp
GROUP BY 
    sales_year
    ,sales_quarter
ORDER BY 
    sales_year
    ,sales_quarter
