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
    description: Trip date
    primary_key: true
    checks:
      - name: not_null
  - name: taxi_type
    type: string
    description: Yellow or green taxi
    primary_key: true
    checks:
      - name: not_null
      - name: accepted_values
        value: ["yellow", "green"]
  - name: payment_type_name
    type: string
    description: Payment method name
    primary_key: true
  - name: trip_count
    type: integer
    description: Number of trips
    checks:
      - name: positive
  - name: total_passengers
    type: integer
    description: Sum of passenger counts
    checks:
      - name: non_negative
  - name: total_distance
    type: float
    description: Sum of trip distances in miles
    checks:
      - name: non_negative
  - name: total_fare
    type: float
    description: Sum of fare amounts in USD
    checks:
      - name: not_null
  - name: total_tips
    type: float
    description: Sum of tip amounts in USD (negative values are refunds)
  - name: total_revenue
    type: float
    description: Sum of total amounts in USD
    checks:
      - name: not_null
  - name: avg_trip_distance
    type: float
    description: Average trip distance in miles
  - name: avg_fare
    type: float
    description: Average fare amount in USD

custom_checks:
  - name: no_duplicate_aggregations
    description: Ensure one row per date/taxi_type/payment_type
    query: |
      SELECT COUNT(*) FROM (
        SELECT pickup_date, taxi_type, payment_type_name
        FROM reports.trips_report
        GROUP BY ALL
        HAVING COUNT(*) > 1
      )
    value: 0

@bruin */

SELECT
    CAST(pickup_datetime AS DATE) AS pickup_date,
    taxi_type,
    payment_type_name,
    COUNT(*)                      AS trip_count,
    SUM(passenger_count)          AS total_passengers,
    SUM(trip_distance)            AS total_distance,
    SUM(fare_amount)              AS total_fare,
    SUM(tip_amount)               AS total_tips,
    SUM(total_amount)             AS total_revenue,
    AVG(trip_distance)            AS avg_trip_distance,
    AVG(fare_amount)              AS avg_fare
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY
    CAST(pickup_datetime AS DATE),
    taxi_type,
    payment_type_name
