# Workshop: dlt (data load tool)

This folder contains my work for the **dlt Workshop** of the Data Engineering Zoomcamp,
focusing on AI-assisted data ingestion using **dlt** (data load tool) and **DuckDB**.

In this workshop, I worked with:

- Setting up the dlt MCP server in Cursor for AI-assisted pipeline development
- Building REST API data pipelines with dlt
- Loading paginated JSON data into DuckDB
- Inspecting pipeline metadata with the dlt Dashboard
- Querying pipeline data via the dlt MCP agent

## Overview

dlt is a Python library that simplifies data loading from APIs to warehouses.
The workshop demonstrated two pipelines:

1. **Demo pipeline** (Open Library API) — scaffolded by `dlt init`, built during the workshop walkthrough
2. **Homework pipeline** (NYC Taxi API) — custom API with no scaffold, built from scratch using Cursor agent

Flow:

Paginated REST API → dlt (Python) → DuckDB (local warehouse) → dlt Dashboard / MCP queries

## Contents

### my-dlt-pipeline/

Demo pipeline from the workshop walkthrough, loading data from the Open Library API.

### taxi-pipeline/

Homework pipeline loading NYC Yellow Taxi trip data from a custom API.

Includes:

- `taxi_pipeline.py` — dlt pipeline fetching paginated taxi data (10,000 records)
- `taxi_pipeline.duckdb` — Local DuckDB database with loaded data
- `pyproject.toml` — Project dependencies

See: [taxi-pipeline/](taxi-pipeline/)

### homework/

Homework solution, including:

- Full setup steps (project init, MCP server, agent prompt)
- dlt Dashboard screenshots
- Agent Q&A exploring the loaded data (tables, columns, row counts, date ranges)
- Answers and SQL queries for all 3 quiz questions with screenshots

See: [homework/README.md](homework/README.md)

## Key Learnings

- How dlt handles extract → normalize → load automatically
- Using `@dlt.resource` with `write_disposition="replace"` for full table reloads
- How dlt creates system tables (`_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`) alongside data tables
- Using the dlt MCP server to ask questions about pipeline metadata via natural language
- The dlt Dashboard for inspecting schemas, tables, and load history
- Handling paginated APIs with Python generators (`yield` pattern)