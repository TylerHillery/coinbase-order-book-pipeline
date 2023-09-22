{{ 
    config(
        materialized='materializedview'
    ) 
}}

with
stg_coinbase_order_book as (
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
        notional_size,
        message_created_at_utc
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
        /*
        The max aggregate function is used to group on product_id so there is only one record 
        per product_id. There should only be one record for each buy and sell before max function is applied. 
        Without the max it would cause their to be two records per product id where either the nbb columns are
        null or the nbo columns are null. 
        */
        --nbb
        max(case when side = 'buy' then price end)                      as nbb_price,
        max(case when side = 'buy' then size end)                       as nbb_size,
        max(case when side = 'buy' then notional_size end)              as nbb_notional_size,
        max(case when side = 'buy' then message_created_at_utc end)     as nbb_last_updated_at_utc,
        --nbo
        max(case when side = 'sell' then price end)                     as nbo_price,
        max(case when side = 'sell' then size end)                      as nbo_size,
        max(case when side = 'sell' then notional_size end)             as nbo_notional_size,
        max(case when side = 'sell' then message_created_at_utc end)    as nbo_last_updated_at_utc
    from
        unioned
    group by
        product_id
),

final as (
    select
        product_id,
        nbb_price,
        nbb_size,
        nbb_notional_size,
        nbb_last_updated_at_utc,
        nbo_price,
        nbo_size,
        nbo_notional_size,
        nbo_last_updated_at_utc,
        (nbb_price + nbo_price) / 2 as nbbo_midpoint
    from
        nbbo
)

select * from final