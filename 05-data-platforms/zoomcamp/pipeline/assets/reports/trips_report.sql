/* @bruin
name: reports.trips_report
type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_date
  time_granularity: date

columns:
  - name: pickup_date
    type: date
    description: Trip date (truncated from pickup_datetime)
    primary_key: true
    checks:
      - name: not_null
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
    primary_key: true
    checks:
      - name: not_null
  - name: payment_type_name
    type: string
    description: Human-readable payment type
    primary_key: true
  - name: trip_count
    type: bigint
    description: Number of trips in this group
    checks:
      - name: not_null
      - name: positive
  - name: total_revenue
    type: float
    description: Sum of total_amount for all trips in this group
    checks:
      - name: non_negative
  - name: avg_fare_amount
    type: float
    description: Average base fare in USD
    checks:
      - name: non_negative
  - name: avg_trip_distance
    type: float
    description: Average trip distance in miles
    checks:
      - name: non_negative
  - name: avg_tip_amount
    type: float
    description: Average tip amount in USD
    checks:
      - name: non_negative

@bruin */

SELECT
    CAST(pickup_datetime AS DATE)   AS pickup_date,
    taxi_type,
    COALESCE(payment_type_name, 'unknown') AS payment_type_name,
    COUNT(*)                        AS trip_count,
    ROUND(SUM(total_amount), 2)     AS total_revenue,
    ROUND(AVG(fare_amount), 2)      AS avg_fare_amount,
    ROUND(AVG(trip_distance), 2)    AS avg_trip_distance,
    ROUND(AVG(tip_amount), 2)       AS avg_tip_amount
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY 1, 2, 3
