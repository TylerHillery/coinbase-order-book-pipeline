{{ 
    config(
        materialized='materializedview'
    ) 
}}

with
stg_coinbase_level2_channel as (
    select * from {{ ref('stg_coinbase_level2_channel') }}
),

nbb as (
    select
        distinct on(product_id) product_id,
        side,
        price,
        size,
        notional_size,
        message_created_at_utc
    from 
        stg_coinbase_level2_channel
    where
        side = 'buy'
    order by
        product_id, price desc
),

nbo as (
    select
        distinct on(product_id) product_id,
        side,
        price,
        size,
        notional_size,
        message_created_at_utc
    from 
        stg_coinbase_level2_channel
    where
        side = 'sell'
    order by
        product_id, price asc
),

unioned as (
    select * from nbb
    union all 
    select * from nbo
)

select * from unioned