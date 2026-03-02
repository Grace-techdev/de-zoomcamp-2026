# Pipeline Summary: NYC Taxi ELT Pipeline

## Overview

An end-to-end ELT pipeline built with Bruin that ingests NYC taxi trip data, cleans and deduplicates it, then aggregates into analytics-ready reports. Uses DuckDB as the local data warehouse.

```
TLC Parquet Files ──→ ingestion.trips (append, raw)
                          │
payment_lookup.csv ──→ ingestion.payment_lookup
                          │
                          ▼
                    staging.trips (time_interval)
                    - Deduplicate (ROW_NUMBER)
                    - Filter nulls
                    - JOIN payment lookup
                          │
                          ▼
                  reports.trips_report (time_interval)
                  - GROUP BY date, taxi_type, payment
                  - SUM/AVG/COUNT metrics
```
## Layer 1: Ingestion (Raw Data Loading)

**Assets:** `ingestion.trips` (Python), `ingestion.payment_lookup` (Seed CSV)

### ingestion.trips

- Fetches raw parquet files from the NYC TLC public endpoint: `https://d37ci6vzurychx.cloudfront.net/trip-data/`
- Downloads one file per taxi type per month (e.g., `yellow_tripdata_2024-01.parquet`)
- Reads `BRUIN_START_DATE` / `BRUIN_END_DATE` to determine which months to fetch
- Reads `taxi_types` variable from `BRUIN_VARS` (default: `["yellow"]`)
- **Minimal transformations** (keeping data as raw as possible):
  - Unifies `tpep_pickup_datetime` / `lpep_pickup_datetime` → `pickup_datetime` (yellow vs green schema difference)
  - Same for `dropoff_datetime`
  - Drops original `tpep_*` / `lpep_*` columns after unification
  - Lowercases all column names to prevent dlt normalization collisions (e.g., `airport_fee` vs `Airport_fee`)
  - Adds `taxi_type` ("yellow" or "green") and `extracted_at` (current timestamp) for lineage
- **Materialization:** `append` — new rows are inserted without touching existing data; duplicates handled downstream

### ingestion.payment_lookup

- Loads a static CSV with 6 payment type mappings (1=Credit card, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided trip)
- **Materialization:** `replace` — fully replaced on each run

### Quality Checks (7)

| Asset | Check | Description |
|---|---|---|
| payment_lookup | not_null(payment_type_id) | Primary key must exist |
| payment_lookup | unique(payment_type_id) | Primary key must be unique |
| payment_lookup | not_null(payment_type_name) | Every ID has a name |
| trips | not_null(pickup_datetime) | Every trip has a pickup time |
| trips | not_null(extracted_at) | Lineage timestamp always set |
| trips | not_null(taxi_type) | Taxi type always assigned |
| trips | accepted_values(taxi_type) | Only "yellow" or "green" |


## Layer 2: Staging (Clean, Deduplicate, Enrich)

**Asset:** `staging.trips` (SQL)

### Transformations

1. **Deduplication:** `ROW_NUMBER()` partitioned by composite key `(pickup_datetime, dropoff_datetime, pulocationid, dolocationid, fare_amount)`, keeps the most recently extracted row (`ORDER BY extracted_at DESC`)
2. **Filtering:** Removes rows with null `dropoff_datetime` (incomplete trip records), and scopes to the Bruin time window (`{{ start_datetime }}` to `{{ end_datetime }}`)
3. **Enrichment:** `LEFT JOIN` with `ingestion.payment_lookup` to resolve numeric `payment_type` → human-readable `payment_type_name` (e.g., 1 → "Credit card")
4. **Column renaming:** `pulocationid` → `pickup_location_id`, `dolocationid` → `dropoff_location_id`

### Materialization

`time_interval` on `pickup_datetime` (timestamp granularity) — Bruin deletes rows in the run's time window, then inserts the query result, enabling incremental reprocessing of any date range.

### Quality Checks (8)

| Check | Description |
|---|---|
| not_null(pickup_datetime) | Primary key, must exist |
| not_null(pickup_location_id) | Primary key, must exist |
| not_null(dropoff_location_id) | Primary key, must exist |
| not_null(fare_amount) | Primary key, must exist |
| non_negative(trip_distance) | Distance cannot be negative |
| not_null(taxi_type) | Taxi type always present |
| accepted_values(taxi_type) | Only "yellow" or "green" |
| custom: no_duplicate_trips | Verifies dedup left zero duplicates |


## Layer 3: Reports (Aggregate for Analytics)

**Asset:** `reports.trips_report` (SQL)

### Aggregation

Groups staging data by `pickup_date`, `taxi_type`, and `payment_type_name`.

| Metric | SQL | Description |
|---|---|---|
| trip_count | `COUNT(*)` | Number of trips |
| total_passengers | `SUM(passenger_count)` | Sum of passengers |
| total_distance | `SUM(trip_distance)` | Total miles traveled |
| total_fare | `SUM(fare_amount)` | Total base fares |
| total_tips | `SUM(tip_amount)` | Total tips |
| total_revenue | `SUM(total_amount)` | Total charges |
| avg_trip_distance | `AVG(trip_distance)` | Average trip distance |
| avg_fare | `AVG(fare_amount)` | Average fare per trip |

### Materialization

`time_interval` on `pickup_date` (date granularity) — consistent with staging so the entire pipeline can be incrementally reprocessed for any date range.

### Quality Checks (9)

| Check | Description |
|---|---|
| not_null(pickup_date) | Date must exist |
| not_null(taxi_type) | Taxi type must exist |
| accepted_values(taxi_type) | Only "yellow" or "green" |
| positive(trip_count) | Every group has at least 1 trip |
| non_negative(total_passengers) | Passenger count >= 0 |
| non_negative(total_distance) | Distance >= 0 |
| not_null(total_fare) | Fare sum always computed |
| not_null(total_revenue) | Revenue sum always computed |
| custom: no_duplicate_aggregations | One row per date/type/payment |


## Total Quality Checks: 24

| Layer | Asset | Count |
|---|---|---|
| Ingestion | payment_lookup | 3 |
| Ingestion | trips | 4 |
| Staging | trips | 8 |
| Reports | trips_report | 9 |
| **Total** | | **24** |


## Common Commands

```bash
# Validate (no execution)
bruin validate ./pipeline/pipeline.yml --environment default

# Run single asset for one month
bruin run --start-date 2024-01-01 --end-date 2024-02-01 --environment default \
  pipeline/assets/ingestion/trips.py

# Run with --full-refresh (first-time table creation for time_interval assets)
bruin run --start-date 2024-01-01 --end-date 2024-02-01 --environment default \
  --full-refresh pipeline/assets/staging/trips.sql

# Query results
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM staging.trips"
bruin query --connection duckdb-default --query "SELECT * FROM reports.trips_report LIMIT 10"
```

## Key Design Decisions

- **Append strategy for ingestion** — raw data is immutable; deduplication happens in staging
- **time_interval strategy for staging/reports** — allows re-processing any date range without full rebuild
- **Composite key for deduplication** — NYC taxi data has no unique row ID, so we use `(pickup_datetime, dropoff_datetime, location_ids, fare_amount)`
- **pickup_datetime as incremental_key** — consistent across all layers; matches how TLC organizes monthly files
- **Negative amounts kept** — `total_amount` and `tip_amount` can be negative (refunds/adjustments); this is real data, not errors
