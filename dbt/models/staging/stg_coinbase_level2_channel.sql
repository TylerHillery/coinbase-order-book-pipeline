{{ 
    config(
        materialized='materializedview'
    ) 
}}

with 
source as (
    select * from {{ source('coinbase', 'level2_channel') }}
),

converted as (
    select convert_from(data, 'utf8') as data from source
),

casted AS (
    select cast(data as jsonb) as data from converted
),

renamed as (
    select
        (data->>'message_type')::string                 as message_type,
        (data->>'message_key')::string                  as message_key,
        (data->>'product_id')::string                   as product_id,
        (data->>'side')::string                         as side,
        (data->>'price')::double                        as price,
        (data->>'size')::double                         as size,
        (data->>'message_created_at_utc')::timestamp    as message_created_at_utc
    from
        casted
),

final as (
    select
        message_type,
        message_key,
        product_id,
        side,
        price,
        size,
        price * size as notional_size,
        message_created_at_utc
    from
        renamed
    where
        size != 0
)

select * from final