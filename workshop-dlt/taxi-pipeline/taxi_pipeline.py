"""
DLT pipeline to load NYC Yellow Taxi trips from a paginated REST API into DuckDB.
"""

import os
import requests
from typing import Generator
import dlt


BASE_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"


def fetch_taxi_data() -> Generator[dict, None, None]:
    page = 1
    printed = False

    while True:
        resp = requests.get(BASE_URL, params={"page": page})
        resp.raise_for_status()
        data = resp.json()

        if not data:
            print(f"Page {page}: empty, stopping.")
            break

        print(f"Page {page}: fetched {len(data)} records")

        if not printed:
            print("First raw record:", data[0])
            printed = True

        for record in data:
            yield record

        page += 1


@dlt.resource(name="taxi_trips", write_disposition="replace")
def taxi_trips():
    yield from fetch_taxi_data()


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="taxi_data",
    )

    print("Starting taxi pipeline load...\n")
    load_info = pipeline.run(taxi_trips())

    print("\nLoad completed!\n")
    print(load_info)
    print("\nDuckDB file:", os.path.abspath("taxi_pipeline.duckdb"))
    print("Next: uv run dlt pipeline taxi_pipeline show")