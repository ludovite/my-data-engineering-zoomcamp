"""
Read all messages from the green-trips topic,
then count how many trips have a trip_distance greater than 5.0 kilometers.
"""

from kafka import KafkaConsumer

from models import Ride


# Set up
topic_name = "green-trips"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[
        "localhost:9092",
    ],
    auto_offset_reset="earliest",
    group_id="rides-console",
    value_deserializer=Ride.deserializer,
    # raise a StopIteration exception after 2 seconds
    # without receiving any value.
    consumer_timeout_ms=2000,
)

# Consume & analyze
count = sum(message.value.trip_distance > 5.0 for message in consumer)

print(f"{count} trips have `trip_distance` > 5.0")

consumer.close()
