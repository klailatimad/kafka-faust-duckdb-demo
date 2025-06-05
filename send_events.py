# save as send_events.py
import json, time, random
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

vehicle_ids = [f"truck_{i}" for i in range(3)]

while True:
    event = {
        "vehicle_id": random.choice(vehicle_ids),
        "timestamp": int(time.time()),
        "lat": 43.7 + random.random() / 100,
        "lon": -79.4 + random.random() / 100,
        "speed_kmh": random.randint(40, 140)
    }
    producer.send("telematics", event)
    print(f"Sent: {event}")
    time.sleep(1)
