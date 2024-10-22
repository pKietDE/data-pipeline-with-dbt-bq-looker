{{ config(
   materialized='table',
   partition_by={
       "field": "date",
       "data_type": "date", 
       "granularity": "day"
   },
   cluster_by=['year', 'month', 'day']
)}}

WITH date_transform AS (
SELECT DISTINCT
   TIMESTAMP_SECONDS(time_stamp) as time_stamp
   ,DATE(TIMESTAMP_SECONDS(time_stamp)) as date
   ,EXTRACT(YEAR FROM TIMESTAMP_SECONDS(time_stamp)) as year
   ,EXTRACT(MONTH FROM TIMESTAMP_SECONDS(time_stamp)) as month
   ,EXTRACT(DAY FROM TIMESTAMP_SECONDS(time_stamp)) as day
FROM {{source('glamira_raw', 'glamira_raw')}}
)
SELECT *
FROM date_transform