# Module 5: Data Platforms with Bruin

This folder contains my work for **Module 5** of the Data Engineering Zoomcamp,
focusing on building end-to-end data pipelines using **Bruin** and **DuckDB**.

In this module, I worked with:

- Installing Bruin CLI and setting up a project with `bruin init`
- Configuring environments and connections in `.bruin.yml`
- Building a layered ELT pipeline (ingestion → staging → reports)
- Writing Python assets for data ingestion (NYC TLC parquet files)
- Writing SQL assets for transformation and aggregation
- Using materialization strategies (`append`, `replace`, `time_interval`)
- Defining quality checks (`not_null`, `unique`, `positive`, `accepted_values`, custom SQL)
- Understanding pipeline variables, dependency graphs, and incremental processing

## Architecture Overview

This module introduces a unified data platform approach where ingestion,
transformation, orchestration, and quality checks live in a single project.

Flow:

NYC TLC Parquet Files → Bruin (Python ingestion) → DuckDB → Bruin (SQL transforms) → Analytics-ready reports

Layers implemented in Bruin:

- **Ingestion layer**
  Raw data loading from TLC public endpoint + static CSV seed

- **Staging layer**
  Deduplication (`ROW_NUMBER`), filtering, and enrichment via payment lookup join

- **Reports layer**
  Daily aggregations grouped by taxi type and payment type

- **Quality checks (24 total)**
  Ensuring data integrity across all layers

## Contents

### my-taxi-pipeline/

Complete Bruin pipeline project for NYC taxi data.

Includes:

- `.bruin.yml` — DuckDB connection configuration
- `pipeline/pipeline.yml` — Pipeline metadata, schedule, and variables
- `pipeline/assets/ingestion/` — Python ingestion asset + CSV seed asset
- `pipeline/assets/staging/` — SQL cleaning and deduplication
- `pipeline/assets/reports/` — SQL aggregation for analytics
- `pipeline-summary.md` — Detailed notes on each layer and quality checks

See: [my-taxi-pipeline/](my-taxi-pipeline/)

### homework/

Homework solution for Module 5, including:

- Pipeline setup documentation and execution commands
- Answers and explanations for all 7 quiz questions
- Topics covered: pipeline structure, materialization strategies, variables, dependencies, quality checks, lineage, and full refresh

See: [homework/README.md](homework/README.md)

## Key Learnings

- How Bruin unifies ingestion, transformation, orchestration, and quality under one CLI
- Difference between `append`, `replace`, `time_interval`, and `view` materialization strategies
- How `time_interval` enables incremental reprocessing without full table rebuilds
- How `--full-refresh` is needed for first-time runs of incremental assets
- How Bruin uses `dlt` under the hood for Python asset data loading
- Handling schema inconsistencies in raw data (column casing, naming conventions)
- Using `bruin validate`, `bruin run`, `bruin lineage`, and `bruin query` in practice
