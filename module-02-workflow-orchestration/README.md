# Module 2: Workflow Orchestration with Kestra

This folder contains my work for **Module 2** of the Data Engineering Zoomcamp, focusing on
building, scheduling, and orchestrating data pipelines using **Kestra**.

In this module, I worked with:
- Task-based workflow orchestration
- Scheduling and backfilling pipelines
- Google Cloud Storage and BigQuery integrations
- External tables vs merged tables in BigQuery
- Basic AI features in Kestra (Copilot & RAG)

## Contents
- `flows/`  
  Kestra workflow definitions used throughout the module, from basic tasks to scheduled GCP pipelines.
- `homework/`  
  Homework solution for Module 2, including:
  - Backfilling 2021 taxi data
  - SQL queries for quiz questions
  - Screenshots and explanations  
  See: `homework/README.md`


## Key Flows

### `08_gcp_taxi.yaml`
This flow is used to **process a single month of taxi data** on demand.

It is parameterized by:
- `taxi` (green / yellow)
- `year`
- `month`

Typical use cases:
- Running ad-hoc executions
- Debugging a specific month
- Inspecting metrics such as file size and row counts

### `09_gcp_taxi_scheduled.yaml`
This is the **scheduled version** of the GCP taxi pipeline.

Key characteristics:
- Uses a `Schedule` trigger to run monthly
- Derives the target file name and table from the trigger execution date
- Supports **Backfill**, allowing historical data to be reprocessed without modifying the flow

This flow was reused in the homework to backfill data for **January–July 2021**.


### `10_chat_without_rag.yaml` / `11_chat_with_rag.yaml`
These flows demonstrate how AI features can be integrated into workflows:
- Querying an LLM without context (hallucination risk)
- Using RAG to ground responses in real documentation

They are included as learning examples and are not part of the homework submission.


## Environment & Configuration Notes

### Google Cloud Authentication

Google Cloud credentials are provided via environment variables rather than Kestra KV Store.

- The GCP service account key is Base64-encoded
- Stored in `.env_encoded`
- Loaded into containers using Docker Compose `env_file`
- Accessed inside Kestra using `secret('GCP_SERVICE_ACCOUNT')`

This approach keeps credentials out of version control and avoids hardcoding secrets in flows.


### External Tables vs Final Tables

The GCP pipelines create:
- **External tables (`*_ext`)** pointing directly to CSV files in GCS
- **Merged tables** in BigQuery that deduplicate records using a generated `unique_row_id`

Some quiz questions intentionally query **external tables** to reflect the raw CSV data,
not the deduplicated final tables.


## Cleanup Notes

After completing this module, the following resources can be safely removed to avoid unnecessary costs:

- BigQuery datasets created for Module 2
- Google Cloud Storage buckets containing taxi CSV files
- Historical Kestra executions (including backfills)

These resources are not required once the module is completed.
