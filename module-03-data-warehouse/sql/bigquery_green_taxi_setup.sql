-- NYC Green Taxi Trip Data (2019–2020)
-- External → Non-partitioned → Partitioned → Partitioned + Clustered

-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `nytaxi.external_green_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://nyc-taxi-data-zoomcamp-2026/green/green_tripdata_2019-*.csv',
    'gs://nyc-taxi-data-zoomcamp-2026/green/green_tripdata_2020-*.csv'
  ]
);

-- Check green trip data
SELECT * FROM nytaxi.external_green_tripdata LIMIT 10;

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE nytaxi.green_tripdata_non_partitioned AS
SELECT * FROM nytaxi.external_green_tripdata;

-- Create a partitioned table from external table
CREATE OR REPLACE TABLE nytaxi.green_tripdata_partitioned
PARTITION BY
  DATE(lpep_pickup_datetime) AS
SELECT * FROM nytaxi.external_green_tripdata;

-- Impact of partition
-- (example month)
SELECT DISTINCT(VendorID)
FROM nytaxi.green_tripdata_non_partitioned
WHERE DATE(lpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

SELECT DISTINCT(VendorID)
FROM nytaxi.green_tripdata_partitioned
WHERE DATE(lpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- Let's look into the partitions
SELECT table_name, partition_id, total_rows
FROM `nytaxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'green_tripdata_partitioned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE nytaxi.green_tripdata_partitioned_clustered
PARTITION BY DATE(lpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM nytaxi.external_green_tripdata;

-- Query scans comparison (example)
SELECT COUNT(*) AS trips
FROM nytaxi.green_tripdata_partitioned
WHERE DATE(lpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID = 1;

SELECT COUNT(*) AS trips
FROM nytaxi.green_tripdata_partitioned_clustered
WHERE DATE(lpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID = 1;