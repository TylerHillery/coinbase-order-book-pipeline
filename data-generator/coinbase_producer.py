import json
from datetime import date, datetime

from kafka import KafkaProducer
from websocket import create_connection

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise "Type %s not serializable" % type(obj)

def format_datetime(datetime_string: str) -> str:
    return (datetime
            .strptime(datetime_string,"%Y-%m-%dT%H:%M:%S.%fZ")
            .strftime("%Y-%m-%d %H:%M:%S")
    )

def coinbase_ws_producer(ws_uri,ws_channels,product_ids):
    prod = KafkaProducer(bootstrap_servers="redpanda:9092") 
    ws = create_connection(ws_uri)
    ws.send(
        json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": product_ids,
                    "channels": ws_channels,
                }
            )
    )

    print(ws.recv()) # first message confirms we have subscribed

    while True:
        message = ws.recv()
        data = json.loads(message)
        if data["type"] == "snapshot":
            
            asks = [{
                    "event_type": "snapshot",
                    "product_id": data["product_id"],
                    "side": "sell",
                    "price": order[0],
                    "size": order[1],
                    "time": format_datetime(data["time"]),
                    "key": data["product_id"] + "-ask-" + str(order[0])
                    } for order in data["asks"]
                ]
            
            bids = [{
                    "event_type": "snapshot",
                    "product_id": data["product_id"],
                    "side": "buy",
                    "price": order[0],
                    "size": order[1],
                    "time": format_datetime(data["time"]),
                    "key": data["product_id"] + "-bid-" + str(order[0])
                    } for order in data["bids"]
                ]
            
            order_book = asks + bids

            for order in order_book:
                prod.send(
                    topic="coinbase_order_book", 
                    key=order["key"].encode("utf-8"),
                    value=json.dumps(order,default=json_serializer,ensure_ascii=False).encode("utf-8")
                )
                print(order) #log
            prod.flush()

        elif data["type"] == "l2update":
            orders = [{
                    "event_type": "l2update",
                    "product_id": data["product_id"],
                    "side": order[0],
                    "price": order[1],
                    "size": order[2],
                    "time": format_datetime(data["time"]),
                    "key": data["product_id"] + "-" + order[0] + "-" + str(order[1])
                    } for order in data["changes"]
                ]
            for order in orders:
                prod.send(
                        topic="coinbase_order_book", 
                        key=order["key"].encode("utf-8"),
                        value=json.dumps(order,default=json_serializer,ensure_ascii=False).encode("utf-8")
                    )
                print(order) #log
            prod.flush()
        else:
            raise Exception(f"Unexpected value for 'type': {data['type']}")

if __name__ == "__main__":
    ws_uri= "wss://ws-feed.exchange.coinbase.com"
    ws_channels = ["level2_batch"]
    product_ids = ["XLM-USD","BTC-USD"]

    coinbase_ws_producer(ws_uri,ws_channels,product_ids)
    