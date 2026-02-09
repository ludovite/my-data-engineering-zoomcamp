# Module 3 : Data Warehousing & BigQuery

We'll practice working with BigQuery and Google Cloud Storage.


## Data

For this homework we will be using the Yellow Taxi Trip Records for January 2024 - June 2024 (not the entire year of data).

Parquet Files are available from the New York City Taxi Data found here:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Loading the data

* GCP configs are inside a `.env` file:
```env
GOOGLE_APPLICATION_CREDENTIALS='/path/to/application_default_credentials.json'
BUCKET_NAME='my-bucket'
BUCKET_LOCATION='europe-west?'
PROJECT_NAME='my_project'
```

* Login via a Service Account (created with Google Cloud console + GCS Admin privileges):
```bash
gcloud auth application-default login
```

* This Python script: [load_yellow_taxi_data.py](./load_yellow_taxi_data.py) loads the data into a GCS bucket.

* BigQuery request to create an external table:
```sql
-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `<project_name>.nytaxi.external_hw3_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://<bucket_name>/yellow_tripdata_2024-*.parquet']
);

-- Create a non partitioned & materialized table from external table
CREATE OR REPLACE TABLE <project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata AS
SELECT * FROM <project_name>.nytaxi.external_hw3_yellow_tripdata
;
```


## Part 1. Counting records

```sql
SELECT COUNT(VendorID)
FROM `<project_name>.nytaxi.external_hw3_yellow_tripdata`
;
```
There are **20,332,093 records** for this dataset.


## Part 2. Data read estimation

This query counts the distinct number of `PULocationIDs` for the entire dataset on both the tables:
```sql
SELECT COUNT(DISTINCT PULocationID)
FROM `<project_name>.nytaxi.external_hw3_yellow_tripdata`
;

SELECT COUNT(DISTINCT PULocationID)
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
;
```
 
As shown by the BQ query tool, the *estimated amount* of data that will be read when this query is executed is 
**0 MB for the External Table** and **155.12 MB for the Materialized Table**.

Big Query cannot guess the amount of data from external table.

## Part 3. Understanding columnar storage

```sql
SELECT PULocationID
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
;  -- Estimation: 155.12 MB


SELECT PULocationID, DOLocationID
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
;  -- Estimation: 310.24 MB
```

A query to retrieve the `PULocationID` from the materialized table consumes about 155 MB of data in BigQuery. Now, a query to retrieve the `PULocationID` and `DOLocationID` on the same table will consume about 310 MB of data (twice). Here is the explanation.

**BigQuery is a columnar database**, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires 
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.


## Part 4. Counting zero fare trips

```sql
SELECT COUNT(fare_amount)
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
WHERE fare_amount = 0
;
```

**8,333 records** have a fare_amount of 0.


## Part 5. Partitioning and clustering

The best strategy to make an optimized table in Big Query if queries always filter based on `tpep_dropoff_datetime` and order the results by `VendorID` is to make **partition by `tpep_dropoff_datetime`** and **cluster on `VendorID`**.

```sql
-- Creating a partition and cluster table
CREATE OR REPLACE TABLE `<project_name>.nytaxi.partitioned_clustered_hw3_yellow_tripdata`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
;
```


## Part 6. Partition benefits

This query retrieves the distinct `VendorID`s between `tpep_dropoff_datetime`
2024-03-01 and 2024-03-15 (inclusive):
```sql
-- from materialized table
SELECT DISTINCT(VendorID)
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
WHERE
  tpep_dropoff_datetime >= TIMESTAMP '2024-03-01'
  AND
  tpep_dropoff_datetime <= TIMESTAMP '2024-03-15'
;  -- Estimated: 310.24 MB

-- from partitioned and clustered table
SELECT DISTINCT(VendorID)
FROM `<project_name>.nytaxi.partitioned_clustered_hw3_yellow_tripdata`
WHERE
  tpep_dropoff_datetime >= TIMESTAMP '2024-03-01'
  AND
  tpep_dropoff_datetime <= TIMESTAMP '2024-03-15'
;  -- Estimated: 26.86 MB
```

The estimated amount of data from BigQuery is in favor of the partitioned table!

**310.24 MB for non-partitioned** table and **26.84 MB for the partitioned** table.


## Part 7. External table storage

Data belonging to the External Table I created is **stored in GCP bucket**.


## Part 8. Clustering best practices

It is best practice in Big Query to always cluster your data:
**False**

The benefits depend on the queries applied. See example in part 6.


## Question 9. Understanding table scans

```sql
SELECT COUNT(*)
FROM `<project_name>.nytaxi.non_partitioned_hw3_yellow_tripdata`
;  - Estimated: 0 B
```
A COUNT(*) without WHERE clause or filters reads no data blocks because **BigQuery uses table metadata** to return the exact row count instantly for materialized tables, **without scanning partitions or clusters**.
