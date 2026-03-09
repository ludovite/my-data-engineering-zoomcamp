# Module 6 Batch Processing with pySpark

For this homework we will be using the Yellow 2025-11 data from the official website:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
```

---

## Part 1: Install Spark and PySpark

Workflow:

- Install Spark: `uv add pyspark`. Java version: `openjdk 17.0.18`.
- Run PySpark
- Create a local spark session:
```python
from pyspark.sql import SparkSession


spark = SparkSession.builder.master("local[*]").appName("test").getOrCreate()

print(f"Spark version: {spark.version}")

df = spark.range(10)
df.show()

spark.stop()
```
- Execute this script.

Here’s the output:

> `Spark version: 4.1.1`

The [marimo file](./Yellow_nov2025_notebook.py) gives answers to the following parts.

---

## Part 2: Yellow November 2025

Workflow:

- Read the November 2025 Yellow into a Spark Dataframe called `df`.
- Repartition the Dataframe to 4 partitions and save it to parquet.

> Average size of the Parquet files created: 25MB.

```
24 MB part-00000-74b6a3c1-8017-435d-883d-534f038e4ee4-c000.snappy.parquet
24 MB part-00001-74b6a3c1-8017-435d-883d-534f038e4ee4-c000.snappy.parquet
24 MB part-00002-74b6a3c1-8017-435d-883d-534f038e4ee4-c000.snappy.parquet
24 MB part-00003-74b6a3c1-8017-435d-883d-534f038e4ee4-c000.snappy.parquet
 0  B _SUCCESS
```

---

## Part 3: Count records

How many taxi trips were there on the 15th of November?

Consider only trips that started on the 15th of November.

we’ll use a SQL query:
```python
df.createOrReplaceTempView("trips")
spark.sql("""
SELECT COUNT(tpep_pickup_datetime)
FROM trips
WHERE 
    DATE(tpep_pickup_datetime) >= '2025-11-15'
    AND DATE(tpep_pickup_datetime) < '2025-11-16'
""").show()
```

> November, 15th had 162,604 trips.

---

## Part 4: Longest trip

What is the length of the longest trip in the dataset in hours?

```python
df_with_duration = (
    df
    .select("tpep_pickup_datetime", "tpep_dropoff_datetime")
    .withColumn("duration_hours",
                F.timestamp_diff(
                    end="tpep_dropoff_datetime",
                    start="tpep_pickup_datetime",
                    unit="SECOND",
                )
                # convert seconds to hours
                / 3_600.0
               )
)
df_with_duration.show(5)

max_duration = df_with_duration.agg(
    F.max("duration_hours")
).collect()[0][0]

print(f"Longest duration: {max_duration:.1f} hours")
```

> The longest trip took 90.6 hours.


## Part 5: User Interface

Spark’s User Interface shows the application’s dashboard at this address: `http://localhost:4040`

> Spark’s UI is at port 4040.

---

## Part 6: Least frequent pickup location zone

The [script](./Yellow_nov2025_notebook.py) loads (and download when not exists) the zone lookup data into a temp view called `zones` in Spark:

```python
lookupdata_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
lookupdata_file =  data_path / "raw" / Path(lookupdata_url.split("/")[-1])

# Download taxi zone lookup data if needed
if not lookupdata_file.is_file():
    print(f"Downloading {lookupdata_url}…")
    response = requests.get(lookupdata_url, timeout=10)
    response.raise_for_status()
    lookupdata_file.write_text(response.text, encoding="utf-8")
    print(f"Writen to {lookupdata_file}")

# Define the schema & create a dataframe
schema_zones = types.StructType([
    types.StructField('LocationID', types.IntegerType(), True),
    types.StructField('Borough', types.StringType(), True),
    types.StructField('Zone', types.StringType(), True),
    types.StructField('service_zone', types.StringType(), True),
])

df_zones = (
    spark.read
    .option("header", "true")
    .schema(schema_zones)
    .csv(str(lookupdata_file))
)
df_zones.createOrReplaceTempView("zones")

# Query the least frequent pickup zone
spark.sql("""
SELECT Zone, COUNT(PULocationID) AS freq
FROM 
    trips AS tr
    INNER JOIN zones AS zo
        ON zo.LocationID = tr.PULocationID
GROUP BY Zone
ORDER BY freq ASC
LIMIT 5
""").show(truncate=False)
```

Using the zone lookup data and the Yellow November 2025 data, we can find the name of the LEAST frequent pickup location Zone:

> Governor's Island/Ellis Island/Liberty Island
> Arden Heights

---
