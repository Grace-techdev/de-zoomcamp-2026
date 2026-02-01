# Module 2 Homework

## Assignment

### Requirement

In this module, the workflows have processed NYC taxi data for the years 2019 and 2020. The goal of this assignment is to extend the existing Kestra pipelines to include data for 2021.

**Dataset**
- Monthly NYC TLC taxi CSV files (green & yellow)
- Green taxi reference:  
  https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download

**Scope**
- Process data from **January 2021 to July 2021**
- Apply to **both green and yellow taxi datasets**

**Approach**

Use Kestra to re-run historical data for 2021, either by:
1. Backfilling the scheduled GCP flow for the relevant date range, or  
2. Manually running the flow per month.

### Solutions

For this assignment, I chose **Approach 1: Backfilling the scheduled flow**.

I reused the existing scheduled workflow **`09_gcp_taxi_scheduled.yaml`**, which processes monthly taxi data based on the trigger execution date.  
Instead of modifying the pipeline or creating new flows, I used Kestra’s **Backfill** feature to reprocess historical data for 2021.


**1. Scheduled flow and triggers**

The scheduled flow defines two triggers:
- One for **green taxi**
- One for **yellow taxi**

These triggers normally run monthly, but they can also be used as the basis for historical backfills.

![Kestra scheduled triggers](../../images/02_backfill_triggers.png)

**2. Backfill configuration**

From the **Triggers** tab, I used **Backfill executions** to re-run the pipeline for historical dates.

Backfill parameters:
- **Start**: `2021-01-01`
- **End**: `2021-08-01`
- **Taxi type**: `green` (repeated for `yellow`)

This configuration creates one execution per month and reuses the same pipeline logic.

![Kestra backfill configuration](../../images/02_backfill_config.png)

**3. BigQuery results**

After the backfill completed, new monthly tables for 2021 were created in BigQuery.

For each month:
- An **external table** (`*_ext`) points directly to the CSV file in GCS
- A **merged table** stores the deduplicated results
![BigQuery tables for 2021](../../images/02_bigquery_2021_tables.png)

**4. Files in Google Cloud Storage**

All corresponding CSV files for 2021 were uploaded to the GCS bucket automatically by the pipeline.

![GCS bucket with 2021 CSV files](../../images/02_gcs_2021_csv_files.png)


**Summary**

By using Kestra backfill on the scheduled workflow:

- No pipeline changes were required
- Historical data for **January–July 2021** was processed consistently
- Both **green** and **yellow** taxi datasets were ingested
- Results can be verified in **BigQuery** and **Cloud Storage**

## Quiz Questions

1) Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?
- 128.3 MiB ✅
- 134.5 MiB
- 364.7 MiB
- 692.6 MiB

**Explanation**

The file size is taken from the execution metrics of the `extract` task in Kestra.

This was obtained by running the flow **`08_gcp_taxi.yaml`** with the following inputs:
- taxi = `yellow`
- year = `2020`
- month = `12`

After the execution finished, I checked the Metrics tab of the run. The upload_to_gcs task reports the size of the uncompressed CSV file in bytes: 134,481,400 bytes
![Yellow taxi 2020-12 CSV file size](../../images/02_q1_yellow_2020_12_file_size.png)


Converting bytes to MiB:
134,481,400 ÷ (1024 × 1024) ≈ 128.3 MiB


2) What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?
- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv` 
- `green_tripdata_2020-04.csv` ✅
- `green_tripdata_04_2020.csv`
- `green_tripdata_2020.csv`

**Solution**
The file variable is defined using Kestra template expressions and is rendered at runtime by replacing each placeholder with the corresponding input value:
- inputs.taxi → green
- inputs.year → 2020
- inputs.month → 04

After rendering, the final value becomes: green_tripdata_2020-04.csv. This matches the naming convention used by the NYC TLC monthly dataset.

**Context for Questions 3–5**

Questions 3–5 are answered by querying **BigQuery external tables** managed by the Kestra GCP pipeline.
Each external table points directly to a monthly CSV file stored in Google Cloud Storage, without loading the data into the final partitioned tables.

3) How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?
- 13,537.299
- 24,648,499 ✅
- 18,324,219
- 29,430,127

**Solution**
```sql
SELECT COUNT(*) AS total_rows
FROM (
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_01_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_02_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_03_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_04_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_05_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_06_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_07_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_08_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_09_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_10_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_11_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.yellow_tripdata_2020_12_ext`
);
```

4) How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?
- 5,327,301
- 936,199
- 1,734,051 ✅
- 1,342,034

**Solution**
```sql
SELECT COUNT(*) AS total_rows
FROM (
  SELECT * FROM `zoomcamp.green_tripdata_2020_01_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_02_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_03_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_04_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_05_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_06_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_07_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_08_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_09_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_10_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_11_ext`
  UNION ALL
  SELECT * FROM `zoomcamp.green_tripdata_2020_12_ext`
);
```

**Note on row counts and query approach (Questions 3–4)**

The row counts in Questions 3 and 4 are calculated from **external tables**, not from the final merged BigQuery tables.

Each external table corresponds to a single monthly CSV file in GCS (e.g. `yellow_tripdata_2020_01_ext`). Since BigQuery does not support wildcard queries across multiple external tables, the total row count for a year is computed by explicitly combining all monthly tables using `UNION ALL`.

This approach ensures the counts reflect the raw CSV data exactly, rather than the deduplicated records stored in the final partitioned tables.

5) How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?
- 1,428,092
- 706,911
- 1,925,152 ✅
- 2,561,031

**Solution**
```sql
SELECT COUNT(*) AS total_rows
FROM `zoomcamp.yellow_tripdata_2021_03_ext`;
```

6) How would you configure the timezone to New York in a Schedule trigger?
- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration  
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration ✅
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration  

**Explanation**

Kestra schedule triggers run in UTC by default.
To align executions with New York local time, the timezone must be explicitly configured.

Using the IANA timezone `America/New_York` ensures the schedule correctly handles daylight saving time transitions. Fixed offsets such as `EST` or `UTC-5` do not account for DST and may result in incorrect execution times.

Example:
```yaml
triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    timezone: America/New_York
    inputs:
      taxi: green
```
