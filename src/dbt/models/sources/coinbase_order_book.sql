{{ config(materialized='source') }}

{% set source_name %}
    {{ mz_generate_name('coinbase_order_book') }}
{% endset %}

CREATE SOURCE {{ source_name }}
FROM KAFKA BROKER 'redpanda:9092' TOPIC 'coinbase_order_book'
  KEY FORMAT BYTES
  VALUE FORMAT BYTES
ENVELOPE UPSERT;