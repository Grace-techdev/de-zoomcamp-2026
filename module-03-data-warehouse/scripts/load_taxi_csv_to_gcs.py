import os
import sys
import gzip
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden

PROJECT_ID = "smooth-ace-486714-u3"                  
BUCKET_NAME = "nyc-taxi-data-zoomcamp-2026"    
CREDENTIALS_FILE = "../secrets/service-account.json"          
DOWNLOAD_DIR = "/tmp/nyc-taxi"

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"
TAXIS = ["yellow", "green"]
YEARS = [2019, 2020]
MONTHS = range(1, 13)
MAX_WORKERS = 6

def get_client():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Missing credentials file: {CREDENTIALS_FILE}")
        sys.exit(1)
    return storage.Client.from_service_account_json(CREDENTIALS_FILE, project=PROJECT_ID)


def ensure_bucket(client: storage.Client) -> storage.Bucket:
    try:
        return client.get_bucket(BUCKET_NAME)
    except NotFound:
        try:
            b = client.bucket(BUCKET_NAME)
            b.location = "US"
            return client.create_bucket(b, project=PROJECT_ID)
        except Forbidden:
            print(f"Bucket name taken or forbidden: {BUCKET_NAME}")
            sys.exit(1)


def blob_exists(bucket: storage.Bucket, name: str) -> bool:
    return storage.Blob(bucket=bucket, name=name).exists(bucket.client)


def download_gz(url: str, gz_path: str) -> str:
    urllib.request.urlretrieve(url, gz_path)
    return gz_path


def gunzip(gz_path: str, csv_path: str) -> str:
    with gzip.open(gz_path, "rb") as f_in, open(csv_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return csv_path


def process_one(bucket: storage.Bucket, taxi: str, year: int, month: int):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ym = f"{year}-{month:02d}"
    csv_name = f"{taxi}_tripdata_{ym}.csv"
    gz_name = f"{csv_name}.gz"
    url = f"{BASE_URL}/{taxi}/{gz_name}"

    gcs_key = f"{taxi}/{csv_name}"
    if blob_exists(bucket, gcs_key):
        return f"SKIP  gs://{bucket.name}/{gcs_key}"

    gz_path = os.path.join(DOWNLOAD_DIR, gz_name)
    csv_path = os.path.join(DOWNLOAD_DIR, csv_name)

    try:
        download_gz(url, gz_path)
        gunzip(gz_path, csv_path)

        blob = bucket.blob(gcs_key)
        blob.upload_from_filename(csv_path)

        return f"OK    gs://{bucket.name}/{gcs_key}"
    finally:
        for p in (gz_path, csv_path):
            if os.path.exists(p):
                os.remove(p)


def main():
    client = get_client()
    bucket = ensure_bucket(client)

    jobs = [(t, y, m) for t in TAXIS for y in YEARS for m in MONTHS]
    print(f"Jobs: {len(jobs)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(process_one, bucket, t, y, m) for (t, y, m) in jobs]
        for fut in as_completed(futs):
            print(fut.result())

    print("Done.")


if __name__ == "__main__":
    main()