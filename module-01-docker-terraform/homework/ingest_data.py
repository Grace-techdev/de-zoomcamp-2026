#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='postgres', help='PostgreSQL user')
@click.option('--pg-pass', default='postgres', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5433, type=int, help='PostgreSQL port (host port)')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--green-table', default='green_trips', help='Target table for green taxi data')
@click.option('--zones-table', default='zones', help='Target table for zones lookup')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for loading')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db,
        green_table, zones_table, chunksize):
    """Ingest Green Taxi (parquet) and Zones (csv) data into PostgreSQL."""

    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    # 1) Load zones lookup 
    zones_file = DATA_DIR / "taxi_zone_lookup.csv"
    zones_df = pd.read_csv(zones_file)

    zones_df.to_sql(
        name=zones_table,
        con=engine,
        if_exists='replace',
        index=False
    )

    print(f"Loaded zones table: {len(zones_df)} rows")

    # 2) Load green taxi trips
    green_file = DATA_DIR / "green_tripdata_2025-11.parquet"
    df = pd.read_parquet(green_file)

    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])

    first = True

    for start in tqdm(range(0, len(df), chunksize)):
        df_chunk = df.iloc[start:start + chunksize]

        df_chunk.to_sql(
            name=green_table,
            con=engine,
            if_exists='replace' if first else 'append',
            index=False
        )

        first = False

    print("Ingest completed successfully.")


if __name__ == '__main__':
    run()