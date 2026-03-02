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
  - name: pickup_datetime
    type: timestamp
    description: Trip pickup timestamp
    primary_key: true
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: timestamp
    description: Trip dropoff timestamp
    primary_key: true
  - name: pickup_location_id
    type: integer
    description: TLC pickup location ID
    primary_key: true
    checks:
      - name: not_null
  - name: dropoff_location_id
    type: integer
    description: TLC dropoff location ID
    primary_key: true
    checks:
      - name: not_null
  - name: fare_amount
    type: float
    description: Base fare in USD
    primary_key: true
    checks:
      - name: not_null
  - name: total_amount
    type: float
    description: Total charge to passenger (negative values are refunds)
  - name: payment_type_name
    type: string
    description: Payment method name from lookup
  - name: trip_distance
    type: float
    description: Trip distance in miles
    checks:
      - name: non_negative
  - name: taxi_type
    type: string
    description: Yellow or green taxi
    checks:
      - name: not_null
      - name: accepted_values
        value: ["yellow", "green"]

custom_checks:
  - name: no_duplicate_trips
    description: Ensure deduplication removed all duplicates
    query: |
      SELECT COUNT(*) FROM (
        SELECT pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id, fare_amount
        FROM staging.trips
        GROUP BY ALL
        HAVING COUNT(*) > 1
      )
    value: 0

@bruin */

WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY
                pickup_datetime,
                dropoff_datetime,
                pulocationid,
                dolocationid,
                fare_amount
            ORDER BY extracted_at DESC
        ) AS row_num
    FROM ingestion.trips
    WHERE pickup_datetime >= '{{ start_datetime }}'
      AND pickup_datetime < '{{ end_datetime }}'
)

SELECT
    d.pickup_datetime,
    d.dropoff_datetime,
    d.pulocationid AS pickup_location_id,
    d.dolocationid AS dropoff_location_id,
    d.passenger_count,
    d.trip_distance,
    d.fare_amount,
    d.tip_amount,
    d.tolls_amount,
    d.total_amount,
    d.payment_type,
    p.payment_type_name,
    d.taxi_type,
    d.extracted_at
FROM deduplicated d
LEFT JOIN ingestion.payment_lookup p
    ON d.payment_type = p.payment_type_id
WHERE d.row_num = 1
  AND d.dropoff_datetime IS NOT NULL
