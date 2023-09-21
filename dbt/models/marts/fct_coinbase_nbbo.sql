{{ 
    config(
        materialized='materializedview'
    ) 
}}

with
stg_coinbase_order_book as (
    select * from {{ ref('stg_coinbase_order_book') }}
),

nbb as (
    select
        distinct on(product_id) product_id,
        side,
        price,
        size,
        notional_size
    from 
        stg_coinbase_order_book
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
        notional_size
    from 
        stg_coinbase_order_book
    where
        side = 'sell'
    order by
        product_id, price asc
),

unioned as (
    select * from nbb
    union all 
    select * from nbo
),

nbbo as (
    select
        product_id,
        --nbb
        max(case when side = 'buy' then price end)          as nbb,
        max(case when side = 'buy' then size end)           as nbb_size,
        max(case when side = 'buy' then notional_size end)  as nbb_notional_size,
        --nbo
        max(case when side = 'sell' then price end)         as nbo,
        max(case when side = 'sell' then size end)          as nbo_size,
        max(case when side = 'sell' then notional_size end) as nbo_notional_size
    from
        unioned
    group by
        product_id
),

final as (
    select
        *,
        (nbb + nbo) / 2 as nbbo_midpoint
    from
        nbbo
)

select * from final