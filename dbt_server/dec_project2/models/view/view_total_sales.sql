WITH sales_total as (
  SELECT 
    dmd.year
    ,dmd.month
    ,SUM(fo.item_price * fo.quantity) as sales_total
  FROM 
    {{ref('fact_order')}} fo 
  INNER JOIN 
    {{ref('dim_date')}} dmd
  ON
    fo.order_date = dmd.time_stamp
  GROUP BY 
    dmd.year
    ,dmd.month
)

SELECT *
FROM sales_total
ORDER BY year,month