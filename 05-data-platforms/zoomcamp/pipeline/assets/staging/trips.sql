/* @bruin
name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp

columns:
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
    primary_key: true
    checks:
      - name: not_null
  - name: pickup_datetime
    type: timestamp
    description: Trip pickup datetime
    primary_key: true
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: timestamp
    description: Trip dropoff datetime
    checks:
      - name: not_null
  - name: pickup_location_id
    type: integer
    description: TLC pickup zone ID
    primary_key: true
    checks:
      - name: not_null
  - name: dropoff_location_id
    type: integer
    description: TLC dropoff zone ID
    primary_key: true
    checks:
      - name: not_null
  - name: fare_amount
    type: float
    description: Base metered fare in USD
    primary_key: true
    checks:
      - name: not_null
      - name: non_negative
  - name: payment_type
    type: integer
    description: Numeric payment type identifier
  - name: payment_type_name
    type: string
    description: Human-readable payment type, joined from payment_lookup
  - name: passenger_count
    type: float
    description: Number of passengers
  - name: trip_distance
    type: float
    description: Trip distance in miles
    checks:
      - name: non_negative
  - name: tip_amount
    type: float
    description: Tip amount in USD
    checks:
      - name: non_negative
  - name: total_amount
    type: float
    description: Total amount charged in USD
    checks:
      - name: non_negative
  - name: extracted_at
    type: timestamp
    description: UTC timestamp when the raw record was extracted

custom_checks:
  - name: no_dropoff_before_pickup
    description: Dropoff datetime must not be earlier than pickup datetime
    query: |
      SELECT COUNT(*)
      FROM staging.trips
      WHERE dropoff_datetime < pickup_datetime
    value: 0

@bruin */

WITH ranked AS (
    SELECT
        taxi_type,
        pickup_datetime,
        dropoff_datetime,
        CAST(PULocationID AS INTEGER)   AS pickup_location_id,
        CAST(DOLocationID AS INTEGER)   AS dropoff_location_id,
        CAST(payment_type AS INTEGER)   AS payment_type,
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        extracted_at,
        ROW_NUMBER() OVER (
            PARTITION BY
                pickup_datetime,
                dropoff_datetime,
                PULocationID,
                DOLocationID,
                fare_amount
            ORDER BY extracted_at DESC
        ) AS rn
    FROM ingestion.trips
    WHERE pickup_datetime >= '{{ start_datetime }}'
      AND pickup_datetime < '{{ end_datetime }}'
      AND pickup_datetime IS NOT NULL
      AND fare_amount >= 0
)
SELECT
    r.taxi_type,
    r.pickup_datetime,
    r.dropoff_datetime,
    r.pickup_location_id,
    r.dropoff_location_id,
    r.payment_type,
    p.payment_type_name,
    r.passenger_count,
    r.trip_distance,
    r.fare_amount,
    r.extra,
    r.mta_tax,
    r.tip_amount,
    r.tolls_amount,
    r.improvement_surcharge,
    r.total_amount,
    r.congestion_surcharge,
    r.extracted_at
FROM ranked r
LEFT JOIN ingestion.payment_lookup p
    ON r.payment_type = p.payment_type_id
WHERE r.rn = 1
