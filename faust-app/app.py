import faust
import duckdb
from pathlib import Path

app = faust.App(
    'telematics-app',
    broker='kafka://kafka:29092',
)

class Telematics(faust.Record, serializer='json'):
    vehicle_id: str
    timestamp: int
    lat: float
    lon: float
    speed_kmh: int

topic = app.topic('telematics', value_type=Telematics)

DUCKDB_PATH = Path("/duckdb-data/telematics.duckdb")

@app.agent(topic)
async def process(stream):
    conn = duckdb.connect(str(DUCKDB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telematics_events (
            event_time TIMESTAMP,
            vehicle_id TEXT,
            timestamp BIGINT,
            lat DOUBLE,
            lon DOUBLE,
            speed_kmh INTEGER
        );
    """)
    
    async for record in stream:
        print(f"{record.vehicle_id} @ {record.lat}, {record.lon} → {record.speed_kmh} km/h")
        conn.execute(
            "INSERT INTO telematics_events VALUES (now(), ?, ?, ?, ?, ?)",
            (record.vehicle_id, record.timestamp, record.lat, record.lon, record.speed_kmh)
        )
