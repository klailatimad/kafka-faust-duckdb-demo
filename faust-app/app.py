import faust
import duckdb
import os

app = faust.App('telematics-app', broker='kafka://kafka:29092')

class Telematics(faust.Record, serializer='json'):
    vehicle_id: str
    timestamp: int
    lat: float
    lon: float
    speed_kmh: int

stream = app.topic('telematics', value_type=Telematics)

# Initialize DuckDB (store in shared volume)
db_path = "/data/telematics.duckdb"
os.makedirs("/data", exist_ok=True)  # Ensure directory exists
con = duckdb.connect(db_path)

# Create table if it doesn't exist
con.execute("""
CREATE TABLE IF NOT EXISTS telematics (
    vehicle_id TEXT,
    timestamp BIGINT,
    lat DOUBLE,
    lon DOUBLE,
    speed_kmh INT
)
""")

@app.agent(stream)
async def process(events):
    async for event in events:
        if event.speed_kmh > 100:
            print(f"{event.vehicle_id} speeding at {event.speed_kmh} km/h!")

        # Save to DuckDB
        con.execute("""
            INSERT INTO telematics VALUES (?, ?, ?, ?, ?)
        """, (event.vehicle_id, event.timestamp, event.lat, event.lon, event.speed_kmh))
