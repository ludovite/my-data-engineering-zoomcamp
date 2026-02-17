{{ config(materialized='table') }}

SELECT *
FROM read_parquet([
    'data/fhv_tripdata_2019_01.parquet',
    'data/fhv_tripdata_2019_02.parquet',
    'data/fhv_tripdata_2019_03.parquet',
    'data/fhv_tripdata_2019_04.parquet',
    'data/fhv_tripdata_2019_05.parquet',
    'data/fhv_tripdata_2019_06.parquet',
    'data/fhv_tripdata_2019_07.parquet',
    'data/fhv_tripdata_2019_08.parquet',
    'data/fhv_tripdata_2019_09.parquet',
    'data/fhv_tripdata_2019_10.parquet',
    'data/fhv_tripdata_2019_11.parquet',
    'data/fhv_tripdata_2019_12.parquet',
    ], filename = true)
