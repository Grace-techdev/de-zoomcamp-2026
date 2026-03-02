# Module 5 Homework: Data Platforms with Bruin

## Setup

Project location:  
[module-05-data-platforms/my-taxi-pipeline](../my-taxi-pipeline)

Initialized the project using the Zoomcamp template:

```bash
bruin init zoomcamp my-taxi-pipeline
cd my-taxi-pipeline
git init  # Bruin requires the project to be a Git repository
```

Configured `.bruin.yml` with a DuckDB connection named `duckdb-default`.

### Pipeline Architecture

The pipeline follows a layered ELT architecture.

**Ingestion Layer**

- [`ingestion/trips.py`](../my-taxi-pipeline/pipeline/assets/ingestion/trips.py)  
  Python asset fetching NYC taxi parquet data from the TLC public endpoint.
- [`ingestion/payment_lookup.asset.yml`](../my-taxi-pipeline/pipeline/assets/ingestion/payment_lookup.asset.yml)  
  Seed asset loading static payment type mappings from CSV.

Materialization:
- `append` for trips (raw ingestion)
- `replace` for payment lookup

**Staging Layer**

- [`staging/trips.sql`](../my-taxi-pipeline/pipeline/assets/staging/trips.sql)

Transformations:
- Deduplication using `ROW_NUMBER()` over composite business key
- Filtering invalid records
- Enrichment via payment lookup join
- `time_interval` materialization on `pickup_datetime`

**Reports Layer**

- [`reports/trips_report.sql`](../my-taxi-pipeline/pipeline/assets/reports/trips_report.sql)

Aggregations:
- Daily metrics
- Grouped by `pickup_date`, `taxi_type`, and `payment_type_name`
- `time_interval` materialization (aligned with staging layer)

### Execution

Validated and executed the pipeline for January 2025:

```bash
# Validate structure and dependencies
bruin validate ./pipeline/pipeline.yml

# Run ingestion layer
bruin run --start-date 2025-01-01 --end-date 2025-02-01 ./pipeline/assets/ingestion/payment_lookup.asset.yml
bruin run --start-date 2025-01-01 --end-date 2025-02-01 ./pipeline/assets/ingestion/trips.py

# Run staging and reports with full refresh (first-time build)
bruin run --start-date 2025-01-01 --end-date 2025-02-01 --full-refresh ./pipeline/assets/staging/trips.sql
bruin run --start-date 2025-01-01 --end-date 2025-02-01 --full-refresh ./pipeline/assets/reports/trips_report.sql
```

### Results

- **4 assets** executed successfully
- **24 quality checks** passed  
  (including `not_null`, `unique`, `positive`, `non_negative`, `accepted_values`, and custom deduplication checks)
- Approximately **7 million rows** ingested for January 2025 (yellow taxi)
- All tables materialized into the local `duckdb.db` database file

The pipeline ran end-to-end successfully with no validation or quality check failures.

## Questions
### Question 1. Bruin Pipeline Structure

In a Bruin project, what are the required files/directories?

- `bruin.yml` and `assets/`
- `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
- `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/` ✅
- `pipeline.yml` and `assets/` only

**Explanation**

A valid Bruin project requires:

- `.bruin.yml` → Defines environments and connection configurations (credentials, platforms, etc.)
- `pipeline/` directory → Contains:
  - `pipeline.yml` → Defines pipeline name, schedule, variables, and default connections
  - `assets/` → Contains all asset definitions (Python, SQL, Seed)

Without `.bruin.yml`, Bruin cannot resolve connections or environments.  
Without `pipeline.yml`, Bruin cannot identify the pipeline structure or execution plan.

### Question 2. Materialization Strategies

You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?

- `append` - always add new rows
- `replace` - truncate and rebuild entirely
- `time_interval` - incremental based on a time column ✅
- `view` - create a virtual table only

**Explanation**

The `time_interval` materialization strategy is designed for incremental processing based on a time column (e.g., `pickup_datetime`).

It works by:

1. Deleting rows within the specified time window (based on the `incremental_key`)
2. Re-inserting fresh results for that same time window

This makes it ideal for:

- Monthly or daily partitioned data
- Reprocessing a specific time range without rebuilding the entire table
- Handling corrections or updates for a given period

Why the other options are incorrect:

- `append` → Always inserts new rows and does not remove existing data. This would create duplicates when reprocessing the same month.
- `replace` → Truncates and rebuilds the entire table every run. Not efficient for large datasets.
- `view` → Creates a virtual table and does not physically store data.

Since NYC taxi data is organized by month using `pickup_datetime`, `time_interval` is the correct incremental strategy.

### Question 3. Pipeline Variables

You have the following variable defined in `pipeline.yml`:

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

How do you override this when running the pipeline to only process yellow taxis?

- `bruin run --taxi-types yellow`
- `bruin run --var taxi_types=yellow`
- `bruin run --var 'taxi_types=["yellow"]'` ✅
- `bruin run --set taxi_types=["yellow"]`

**Explanation**

The variable `taxi_types` is defined as an array of strings.

When overriding variables via the CLI, Bruin expects values to be passed as valid JSON.

Since `taxi_types` is an array, we must pass a JSON array:

```bash
--var 'taxi_types=["yellow"]'
```

Single quotes are required so the shell correctly interprets the JSON string.

### Question 4. Running with Dependencies

You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

- `bruin run ingestion.trips --all`
- `bruin run ingestion/trips.py --downstream` ✅
- `bruin run pipeline/trips.py --recursive`
- `bruin run --select ingestion.trips+`

**Explanation**

Bruin executes assets as a dependency graph (DAG).

The `--downstream` flag runs the selected asset and all assets that depend on it.

Since:

- `staging.trips` depends on `ingestion.trips`
- `reports.trips_report` depends on `staging.trips`

Using:

```bash
bruin run ingestion/trips.py --downstream
```

ensures the ingestion layer and all dependent layers execute in the correct order.

### Question 5. Quality Checks

You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

- `name: unique`
- `name: not_null` ✅
- `name: positive`
- `name: accepted_values, value: [not_null]`

**Explanation**

The `not_null` check ensures that a column does not contain any NULL values.

Since `pickup_datetime` is a required field (and often used as an incremental key), it must always have a value. Adding a `not_null` check guarantees data integrity and prevents incomplete records from being accepted.

### Question 6. Lineage and Dependencies

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- `bruin graph`
- `bruin dependencies`
- `bruin lineage` ✅
- `bruin show`

**Explanation**

The `bruin lineage` command visualizes the dependency graph (DAG) of the pipeline.

It shows upstream and downstream relationships between assets, helping you understand how data flows across ingestion, staging, and reporting layers.

The other options are not valid commands for visualizing dependency graphs.

### Question 7. First-Time Run

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- `--create`
- `--init`
- `--full-refresh` ✅
- `--truncate`

**Explanation**

The `--full-refresh` flag forces Bruin to rebuild tables from scratch.

For assets using incremental strategies like `time_interval`, this ensures:

- Existing tables are recreated
- Data is fully reprocessed
- No previous state affects the results

This is recommended for first-time runs or when resetting a pipeline.