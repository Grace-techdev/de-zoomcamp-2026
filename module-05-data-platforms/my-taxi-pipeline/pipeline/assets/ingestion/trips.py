"""@bruin

name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: Trip pickup timestamp (unified from tpep/lpep)
    checks:
      - name: not_null
  - name: extracted_at
    type: timestamp
    description: When this row was extracted
    checks:
      - name: not_null
  - name: taxi_type
    type: string
    description: Yellow or green taxi
    checks:
      - name: not_null
      - name: accepted_values
        value: ["yellow", "green"]

@bruin"""

import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"


def generate_months_to_ingest():
    """Parse BRUIN_START_DATE / BRUIN_END_DATE and yield (year, month) tuples."""
    start_date = os.environ.get("BRUIN_START_DATE", "2022-01-01")
    end_date = os.environ.get("BRUIN_END_DATE", "2022-01-31")

    start = datetime.strptime(start_date, "%Y-%m-%d").replace(day=1)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(day=1)

    current = start
    while current <= end:
        yield current.year, current.month
        current += relativedelta(months=1)


def build_parquet_url(taxi_type: str, year: int, month: int) -> str:
    """Build the TLC parquet file URL for a given taxi type and month."""
    filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    return f"{BASE_URL}{filename}"


def fetch_trip_data(url: str, taxi_type: str) -> pd.DataFrame:
    """Download a single parquet file and normalize the pickup datetime column."""
    df = pd.read_parquet(url)

    if "tpep_pickup_datetime" in df.columns:
        df["pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
        df["dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
        df = df.drop(columns=["tpep_pickup_datetime", "tpep_dropoff_datetime"])
    elif "lpep_pickup_datetime" in df.columns:
        df["pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
        df["dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
        df = df.drop(columns=["lpep_pickup_datetime", "lpep_dropoff_datetime"])
    else:
        raise ValueError(f"No pickup datetime column found in {taxi_type} data")

    # Normalize all column names to lowercase to avoid dlt NameNormalizationCollision
    # (e.g. some months have 'airport_fee', others have 'Airport_fee')
    df.columns = df.columns.str.lower()
    # Drop any columns that became duplicates after lowercasing
    df = df.loc[:, ~df.columns.duplicated()]

    df["taxi_type"] = taxi_type
    return df


def materialize():
    """Fetch NYC taxi trip data and return a single DataFrame for Bruin to load."""
    vars_str = os.environ.get("BRUIN_VARS", "{}")
    try:
        taxi_types = json.loads(vars_str).get("taxi_types", ["yellow"])
    except (json.JSONDecodeError, TypeError):
        taxi_types = ["yellow"]

    extracted_at = datetime.utcnow()
    frames = []

    for taxi_type in taxi_types:
        for year, month in generate_months_to_ingest():
            url = build_parquet_url(taxi_type, year, month)
            try:
                df = fetch_trip_data(url, taxi_type)
                df["extracted_at"] = extracted_at
                frames.append(df)
            except Exception as e:
                print(f"Skipping {url}: {e}")
                continue

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
