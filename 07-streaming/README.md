# Module 7 - Stream Processing

We’ll practice streaming with Kafka (Redpanda) and PyFlink.

We use Redpanda, a drop-in replacement for Kafka. It implements the same
protocol, so any Kafka client library works with it unchanged.

For this homework we will be using Green Taxi Trip data from October 2025:

- [green_tripdata_2025-10.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet)


## Setup

We'll use the same infrastructure from the [workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming/workshop).

Follow the setup instructions: build the [Docker image](./docker-compose.yml), start the services:

```bash
docker compose build
docker compose up -d
```

This gives us:

- Redpanda (Kafka-compatible broker) on `localhost:9092`
- Flink Job Manager at http://localhost:8081
- Flink Task Manager
- PostgreSQL on `localhost:5432` (user: `postgres`, password: `postgres`)

Python tasks use a refactored `Ride` class from the [models file](./src/models.py). It contains:

- some usefull columns from the dataset (see Question 2);
- a serialization to JSON data as a method;
- a deserialization from JSON.

In order to get access to that module, one needs to add `src/` folder to the PYTHONPATH. I recommend [direnv](https://direnv.net/) utility.


## Question 1. Redpanda version

Run `rpk version` inside the Redpanda container:

```bash
docker exec -it 07-streaming-redpanda-1 rpk version
```

What version of Redpanda are you running?

> `rpk version: v25.3.9`


## Question 2. Sending data to Redpanda

Create a topic called `green-trips`:

```bash
docker exec -it 07-streaming-redpanda-1 rpk topic create green-trips
```

Now write a producer to send the green taxi data to this topic.

Read the parquet file and keep only these columns:

- `lpep_pickup_datetime`
- `lpep_dropoff_datetime`
- `PULocationID`
- `DOLocationID`
- `passenger_count`
- `trip_distance`
- `tip_amount`
- `total_amount`

Convert each row to a dictionary and send it to the `green-trips` topic.
You’ll need to handle the datetime columns - convert them to strings
before serializing to JSON.

Measure the time it takes to send the entire dataset and flush:
Code [here](./src/producers/producer.py).

How long did it take to send the data?

```python3
uv run python src/producers/producer.py
```

> 10 seconds


## Question 3. Consumer - trip distance

Write a Kafka consumer that reads all messages from the `green-trips` topic
(set `auto_offset_reset='earliest'`).

Count how many trips have a `trip_distance` greater than 5.0 kilometers.

How many trips have `trip_distance` > 5?
Code [here](./src/consumers/consumer_trip_distance.py).

```python3
uv run python src/consumers/consumer_trip_distance.py
```

> 8,506


## Part 2: PyFlink (Questions 4-6)

Tables published by pyFlink are created from the docker compose file into PostgreSQL database. See `*_init.sql` files.

Important notes for the Flink jobs:

- Job files are located in `workshop/src/job/` - this directory is
  mounted into the Flink containers at `/opt/src/job/`
- Submit jobs with:
  `docker exec -it 07-streaming-jobmanager-1 flink run -py /opt/src/job/your_job.py`
- The `green-trips` topic has 1 partition, so parallelism is set to 1
  in Flink jobs (`env.set_parallelism(1)`). With higher parallelism,
  idle consumer subtasks prevent the watermark from advancing.
- Flink streaming jobs run continuously. Let the job run for a minute
  or two until results appear in PostgreSQL, then query the results.
  One can cancel the job from the Flink UI at http://localhost:8081
- If data are sent to the topic multiple times, delete and recreate
  the topic to avoid duplicates:
  `docker exec -it 07-streaming-redpanda-1 rpk topic delete green-trips`


## Question 4. Tumbling window - pickup location

Init SQL table creation is [here](./aggregated_pickup_init.sql).

I created a [Flink job](./src/job/pickup_location_job.py) that reads from `green-trips` and uses a 5-minute
tumbling window to count trips per `PU_location_id`, 
and writes the results to a PostgreSQL table with columns:
`window_start`, `PU_location_id`, `num_trips`.

After the job processes all data, query the results:

```sql
SELECT PU_location_id, num_trips
FROM aggregated_pickup
ORDER BY num_trips DESC
LIMIT 3;
```

Which `PU_location_id` had the most trips in a single 5-minute window?

> 74


## Question 5. Session window - longest streak

Init SQL table creation is [here](./aggregated_streak_init.sql).

I created another [Flink job](./src/job/longest_streak_job.py) that uses a session window with a 5-minute gap
on `PU_location_id`, using `lpep_pickup_datetime` as the event time
with a 5-second watermark tolerance.

A session window groups events that arrive within 5 minutes of each other.
When there’s a gap of more than 5 minutes, the window closes.

Write the results to a PostgreSQL table and find the `PU_location_id`
with the longest session (most trips in a single session).

How many trips were in the longest session?

```sql
SELECT window_start, window_end, pu_location_id, num_trips
FROM aggregated_streak
ORDER BY num_trips DESC
LIMIT 3;
```

> 81


## Question 6. Tumbling window - largest tip

Init SQL table creation is [here](./aggregated_tips_init.sql).

I created a [Flink job](./src/job/tips_per_hour_job.py) that uses a 1-hour tumbling window to compute the
total `tip_amount` per hour (across all locations).

Which hour had the highest total tip amount?
```sql
SELECT *
FROM aggregated_tips
ORDER BY total_tips DESC
LIMIT 5;
```

> 2025-10-16 18:00:00
