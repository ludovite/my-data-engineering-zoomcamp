"""
Produce data for kafa
"""

import time

from kafka import KafkaProducer
import pandas as pd

from models import Ride


# Import data
data_file = "data/green_tripdata_2025-10.parquet"
columns = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
    "total_amount",
]

df = pd.read_parquet("data/green_tripdata_2025-10.parquet", columns=columns).astype(
    {"passenger_count": "Int64"}
)

# Set up Kafka
topic_name = "green-trips"
producer = KafkaProducer(
    bootstrap_servers=[
        "localhost:9092",
    ],
    value_serializer=Ride.serializer,
)

# Send values
t0 = time.time()

# iter = 10
for _, row in df.iterrows():
    # iter -= 1
    # if iter <= 0:
    #     break
    ride = Ride.from_row(row)
    producer.send(topic_name, value=ride)
    # print(f"Sent: {ride}")
    # time.sleep(0.01)

producer.flush()

t1 = time.time()
print(f"took {(t1 - t0):.2f} seconds")
