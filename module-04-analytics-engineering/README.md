# Module 4: Analytics Engineering with dbt

This folder contains my work for **Module 4** of the Data Engineering Zoomcamp,  
focusing on analytics engineering using **dbt Cloud + BigQuery**.

In this module, I transformed raw NYC Taxi datasets into analytics-ready models using dbt, following a layered transformation approach.

In this module, I worked with:

- Connecting dbt Cloud to BigQuery
- Structuring a dbt project (staging → intermediate → marts)
- Building fact and dimension models
- Writing generic and custom data tests
- Understanding lineage and DAG execution
- Running production deployment jobs
- Extending the warehouse with additional FHV data

## Architecture Overview

This module builds on top of the BigQuery warehouse created in Module 3.

Flow:

GCS → BigQuery (raw tables) → dbt (transformations) → Analytics-ready marts

Layers implemented in dbt:

- **Staging models**  
  Clean, standardize, and cast raw taxi data

- **Intermediate models**  
  Combine Green and Yellow datasets and apply business logic

- **Marts (Fact & Dimension models)**  
  - `fct_trips`
  - `fct_monthly_zone_revenue`
  - `dim_zones`
  - `dim_vendors`

- **Data tests & documentation**  
  Ensuring schema integrity and data quality


## Contents

### homework/

Homework solution for Module 4, including:

- Full dbt Cloud setup (DEV & PROD environments)
- Production deployment job configuration
- SQL queries and screenshots for all quiz questions
- Implementation of FHV 2019 staging model
- Record validation and result verification in BigQuery

See:  
[homework/README.md](homework/README.md)

### taxi_rides_ny/

Complete dbt project used in this module.

Includes:

- `models/`
  - staging/
  - intermediate/
  - marts/
- `macros/`
- `seeds/`
- `packages.yml`
- `dbt_project.yml`

This project was originally developed in dbt Cloud and later exported to this repository for reproducibility.

### scripts/

Python utilities used to extend the warehouse with additional datasets:

- `load_fhv_2019_to_gcs.py`  
  Downloads FHV 2019 data, decompresses it, and uploads to GCS.

This data was then:
- Loaded into BigQuery
- Modeled via `stg_fhv_tripdata` in dbt

## Key Learnings

- Difference between `dbt run`, `dbt test`, and `dbt build`
- How `--select` works and how graph operators (`+model+`) affect lineage execution
- How generic tests (e.g. `accepted_values`) enforce data contracts
- Importance of separating Development and Production environments
- How dbt deployment jobs integrate with Git branches
- How analytics engineering formalizes the “T” in ELT