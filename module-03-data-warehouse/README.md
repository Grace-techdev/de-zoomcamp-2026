# Module 3: Data Warehousing & BigQuery

This folder contains my work for **Module 3** of the Data Engineering Zoomcamp,
focusing on building and optimizing a data warehouse using Google BigQuery.

In this module, I worked with:
- Loading large-scale NYC Taxi datasets into Google Cloud Storage
- Creating external tables in BigQuery from GCS data
- Building materialized (managed) tables in BigQuery
- Understanding columnar storage and how it affects query cost
- Using partitioning and clustering to optimize query performance
- Analyzing query execution and bytes scanned in BigQuery

## Contents

### homework/
Homework solution for Module 3, including:
- Loading Yellow Taxi Trip data (Jan–Jun 2024) into GCS using Python
- Creating external and materialized BigQuery tables
- Query cost estimation and optimization analysis
- Partitioning and clustering experiments
- SQL queries, screenshots, and explanations for all quiz questions

See: [homework/README.md](homework/README.md)

### scripts/
Python scripts used to load NYC Yellow and Green Taxi data (2019–2020) into
Google Cloud Storage.

These datasets are used for:
- BigQuery performance experiments in Module 3
- Preparing the warehouse for Module 4 (Analytics Engineering with dbt)

### sql/
BigQuery SQL scripts used throughout the module:

- [`bigquery_yellow_taxi_setup.sql`](sql/bigquery_yellow_taxi_setup.sql)  
  External → non-partitioned → partitioned → partitioned & clustered tables
  for Yellow Taxi data (2019–2020)

- [`bigquery_green_taxi_setup.sql`](sql/bigquery_green_taxi_setup.sql)  
  Same table setup flow for Green Taxi data (2019–2020)

- [`big_query_ml.sql`](sql/big_query_ml.sql)  
  A simple BigQuery ML example for predicting taxi tips  
  (included for learning purposes)