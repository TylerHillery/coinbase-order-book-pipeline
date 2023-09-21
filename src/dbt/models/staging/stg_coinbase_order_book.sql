{{ 
    config(
        materialized='view'
    ) 
}}

with 
source as (
    select * from {{ source('redpanda', 'coinbase_order_book') }}
),

converted as (
    select convert_from(data, 'utf8') as data from source
),

casted AS (
    select cast(data as jsonb) as data from converted
),

renamed AS (

    select
        (data->>'event_type')::string   as event_type,
        (data->>'product_id')::string   as product_id,
        (data->>'side')::string         as side,
        (data->>'price')::double        as price,
        (data->>'size')::double         as size,
        (data->>'time')::timestamp      as event_created_at,
        (data->>'key')::string          as key
    from
        casted
),

final as (
    select
        *,
        price * size as notional_size
    from
        renamed
    where
        size != 0
)

select * from final