{{ config(materialized='source') }}

CREATE SOURCE {{ this }}
FROM KAFKA BROKER 'redpanda:9092' TOPIC 'coinbase_level2_channel'
  KEY FORMAT BYTES
  VALUE FORMAT BYTES
ENVELOPE UPSERT;