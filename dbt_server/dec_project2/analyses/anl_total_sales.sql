WITH all_months AS (
  SELECT DISTINCT
    year,
    month
  FROM {{ref('dim_date')}}
),

monthly_sales AS (
  SELECT 
    dmd.year,
    dmd.month,
    SUM(fo.item_price * fo.quantity) as sales_total
  FROM {{ref('fact_order')}} fo
  INNER JOIN {{ref('dim_date')}} dmd
    ON fo.order_date = dmd.time_stamp
  GROUP BY dmd.year, dmd.month
)

SELECT 
  am.year,
  am.month,
  {{handle_null("ms.sales_total",0)}} as sales_total
FROM all_months am
LEFT JOIN monthly_sales ms
  ON am.year = ms.year AND am.month = ms.month
ORDER BY am.year, am.month