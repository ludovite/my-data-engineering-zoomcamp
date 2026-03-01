"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
  - name: pickup_datetime
    type: timestamp
    description: Trip pickup datetime, normalized from tpep_/lpep_ source columns
  - name: dropoff_datetime
    type: timestamp
    description: Trip dropoff datetime, normalized from tpep_/lpep_ source columns
  - name: passenger_count
    type: float
    description: Number of passengers
  - name: trip_distance
    type: float
    description: Trip distance in miles
  - name: payment_type
    type: integer
    description: Payment type identifier
  - name: fare_amount
    type: float
    description: Base metered fare
  - name: total_amount
    type: float
    description: Total amount charged
  - name: extracted_at
    type: timestamp
    description: UTC timestamp when this batch was extracted
@bruin"""

import io
import json
import os
from datetime import date

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta


def materialize():
    start_date = date.fromisoformat(os.environ["BRUIN_START_DATE"])
    end_date = date.fromisoformat(os.environ["BRUIN_END_DATE"])
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get(
        "taxi_types", ["yellow", "green"]
    )

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    extracted_at = pd.Timestamp.utcnow()

    frames = []
    current = start_date.replace(day=1)

    while current <= end_date:
        month_str = current.strftime("%Y-%m")
        for taxi_type in taxi_types:
            url = f"{base_url}/{taxi_type}_tripdata_{month_str}.parquet"
            print(f"Fetching {url}")
            try:
                response = requests.get(url, timeout=120)
                response.raise_for_status()
                df = pd.read_parquet(io.BytesIO(response.content))

                # Normalize pickup/dropoff column names across yellow and green schemas
                if "tpep_pickup_datetime" in df.columns:
                    df = df.rename(columns={
                        "tpep_pickup_datetime": "pickup_datetime",
                        "tpep_dropoff_datetime": "dropoff_datetime",
                    })
                elif "lpep_pickup_datetime" in df.columns:
                    df = df.rename(columns={
                        "lpep_pickup_datetime": "pickup_datetime",
                        "lpep_dropoff_datetime": "dropoff_datetime",
                    })

                df["taxi_type"] = taxi_type
                df["extracted_at"] = extracted_at
                frames.append(df)
                print(f"  -> {len(df):,} rows")
            except Exception as e:
                print(f"Warning: could not fetch {url}: {e}")

        current += relativedelta(months=1)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
