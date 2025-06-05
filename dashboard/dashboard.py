import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path
import shutil

st.set_page_config(page_title="Telematics Dashboard", layout="wide")

st.title("🚚 Live Telematics Dashboard")

DUCKDB_PATH = Path("/duckdb-data/telematics.duckdb")

# Load data
@st.cache_data(ttl=5)
def load_data():
    temp_path = "/tmp/telematics_read.duckdb"
    shutil.copyfile(DUCKDB_PATH, temp_path)
    conn = duckdb.connect(temp_path, read_only=True)
    df = conn.execute("SELECT * FROM telematics_events ORDER BY event_time DESC LIMIT 500").df()
    return df

df = load_data()

if df.empty:
    st.warning("No data available yet. Keep the producer running.")
else:
    vehicle_ids = df["vehicle_id"].unique()
    selected_ids = st.multiselect("Select Vehicles", vehicle_ids, default=list(vehicle_ids))

    filtered_df = df[df["vehicle_id"].isin(selected_ids)]

    st.map(filtered_df.rename(columns={"lat": "latitude", "lon": "longitude"}))

    st.line_chart(filtered_df.set_index("event_time")[["speed_kmh"]])
    st.dataframe(filtered_df)
