{{ 
    config(
        materialized='materializedview'
    ) 
}}

with
bin_records as (
    select
        product_id,
        side,
        round(price) as rounded_price,
        sum(size) as size
    from 
        {{ ref('stg_coinbase_level2_channel') }}
    group by
        product_id,
        side,
        rounded_price
),
buy_cumulative_size as (
select
    bin_records.product_id,
    bin_records.side,
    bin_records.rounded_price,
    sum(running_total.size) as cumulative_size
from
    bin_records
    inner join bin_records as running_total
        on bin_records.product_id = running_total.product_id
        and bin_records.side = running_total.side
        and bin_records.rounded_price <= running_total.rounded_price
where
    bin_records.side = 'buy'
group by
    bin_records.product_id,
    bin_records.side,
    bin_records.rounded_price
),
sell_cumulative_size as (
select
    bin_records.product_id,
    bin_records.side,
    bin_records.rounded_price,
    sum(running_total.size) as cumulative_size
from
    bin_records
    inner join bin_records as running_total
        on bin_records.product_id = running_total.product_id
        and bin_records.side = running_total.side
        and bin_records.rounded_price >= running_total.rounded_price
where
    bin_records.side = 'sell'
group by
    bin_records.product_id,
    bin_records.side,
    bin_records.rounded_price
)
select * from buy_cumulative_size
union all 
select * from sell_cumulative_size