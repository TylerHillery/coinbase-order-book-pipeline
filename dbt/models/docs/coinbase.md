<!-- Tables -->
{% docs source_coinbase_level2_channel %}
The Coinbase level2 channel provides a summarized view of all the buy and sell orders for securities on their exchange. One record represents a product_id (BTC-USD), price_level (20000.00000) and side (bid, ask). 

The data is ingested from the [Coinbase websocket feed](https://docs.cloud.coinbase.com/exchange/docs/websocket-channels#level2-batch-channel) using the Level2 Batch Channel which delivers Level 2 data in batches every 50 milliseconds.

The data is inserted via the [ENVELOPE UPSERT](https://materialize.com/docs/sql/create-source/kafka/#handling-upserts) which handles updates, deletes, and inserts based on the message_key of the message (product_id + price + side). 

Updates for records will have a different `size` amount which specifies the total amount people are willing to buy/sell for the product_id at that given price level. The size property is the updated size at the price level, not a delta. A size of `0` indicates the price level can be removed.

Here is an example request sent to the Websocket feed to subscribe to this channel:
```json
// Request
{
    "type": "subscribe",
    "product_ids": [
        "ETH-USD",
        "BTC-USD"
    ],
    "channels": ["level2_batch"]
}
```
{% enddocs %}

<!-- Columns -->
{% docs message_type %}
Represents the type of event sent from the Coinbase Level2 Batch Channel. There are two types of events: `snapshot` and `l2update`.

`snapshot` will be the first message sent after subscribing which provides an overview of the orderbook:

```json
{
    {
    "type": "snapshot",
    "product_id": "BTC-USD",
    "bids": [["10101.10", "0.45054140"]],
    "asks": [["10102.55", "0.57753524"]]
    },
    {
    "type": "snapshot",
    "product_id": "ETH-USD",
    "bids": [["10101.10", "0.45054140"]],
    "asks": [["10102.55", "0.57753524"]]
    }
}
```

`l2update` stands for level 2 update and will provide a message if the `size` has changed at a given price level for the product_id. The message provides the new size, not the change in size. The `changes` message_key provides a list which corresponds to `[side, price, size]`

```json
{
  "type": "l2update",
  "product_id": "BTC-USD",
  "time": "2019-08-14T20:42:27.265Z",
  "changes": [
    [
      "buy",
      "10101.80000000", 
      "0.162567"
    ]
  ]
}
```
{% enddocs %}

{% docs product_id %}
The id to identify the security e.g. `BTC-USD`
{% enddocs %}

{% docs message_key %}
Used as the `key` for the `ENVELOPE UPSERT` ingestion method which means it should be unique. If the append only ingestion method was used the message_key + message_created_at_utc would make up the unique key where the max message_created_at_utc value for each message_key would represent the current record. 
{% enddocs %}

{% docs side %}
The side of the order which can be `buy` or `sell`. Sometimes referred to as `bid` or `ask`. 
{% enddocs %}

{% docs price %}
The price of the security. Denomination is determined by the product_id. For example, if the product_id is BTC-USD, the price is denominated in USD.
{% enddocs %}

{% docs size %}
Specifies the total amount people are willing to buy/sell for the product_id at that given price level.
{% enddocs %}

{% docs notional_size %}
Specifies the total notional amount people are willing to buy/sell for the product_id at that given price level. Calculated by taking `price * size`
{% enddocs %}

{% docs message_created_at_utc %}
The time property is the time of the event as recorded by our trading engine. The formatted is converted from `%Y-%m-%dT%H:%M:%S.%fZ` to `%Y-%m-%d %H:%M:%S` before being ingested to match the expected format of timestamps for Materialize DB. The timezone is UTC. 
{% enddocs %}

{% docs nbbo_price %}
Represents either the highest buy price someone is willing to buy the security at or the lowest sell price someone is willing to sell the security at. 
{% enddocs %}

{% docs nbbo_size %}
Represents the size for the given nbb_price or nbo_price
{% enddocs %}

{% docs nbbo_notional_size %}
Represents the notional size for the given nbb_price or nbo_price
{% enddocs %}

{% docs nbbo_last_updated_at_utc %}
Represents the last time the nbo or nbb was updated/changed.
{% enddocs %}

{% docs nbbo_midpoint %}
The middle price between the nbb_price and nbo_price. Calculated by
`(nbb_price + nbo_price) / 2`
{% enddocs %}