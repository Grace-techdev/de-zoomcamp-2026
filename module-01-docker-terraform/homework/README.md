# Module 1 Homework: Docker & SQL

This README contains my solutions for Module 1 of the Data Engineering Zoomcamp.

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

- 25.3 ✅
- 24.3.1
- 24.2.1
- 23.3.1

**Solution: 25.3**

Step 1: Run the `python:3.13` image with `bash` as the entrypoint
```
docker run -it --rm --entrypoint=bash python:3.13
```
Step 2: Inside the container, check the pip version
```
root@dfc2fcc502e8:/# pip --version
```
Output:
```
pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432 
- db:5432 ✅

**Solution: db:5432**

Containers within the same Docker Compose network communicate using the **service name** and the **container's internal port**.

From the `docker-compose.yaml`:
- The Postgres service name is `db`
- Postgres listens on port `5432` inside the container
- The port mapping `5433:5432` is only used for host-to-container access

Since pgAdmin runs in the same Docker network as Postgres, it should connect using the service name (`db`) and the internal Postgres port (`5432`).

## Prepare the Data (Q3–Q6)

The goal is to load the datasets into PostgreSQL (running in Docker) so I can query them with SQL in pgAdmin.

**Step 1: Start PostgreSQL + pgAdmin with Docker Compose**

From the `homework` folder (where `docker-compose.yaml` lives):

```
docker compose up -d
docker compose ps
```

Expected ports:
- postgres: 5433 -> 5432
- pgAdmin: 8080 -> 80

**Step 2: Download the datasets**

Create a local data/ folder under homework/ and download:
```
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```
**Step 3: Run ingestion**
Initialize uv and install deps once:
```
uv init --python=3.13
uv add pandas pyarrow sqlalchemy psycopg2-binary tqdm click
```
Run the ingestion script (loads two tables into Postgres):
- green_trips (from parquet)
- zones (from csv)
```
uv run python homework/ingest_data.py
```

**Step 4: Open pgAdmin and verify the tables**

Forward port 8080 and open it in the browser.

Login:
- Email: pgadmin@pgadmin.com
- Password: pgadmin

Register a server (pgAdmin -> Register -> Server):
- Host name/address: db
- Port: 5432
- Maintenance database: ny_taxi
- Username: postgres
- Password: postgres

Quick verification in Query Tool:
```sql
SELECT COUNT(*) FROM green_trips;
SELECT COUNT(*) FROM zones;
```

## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- 7,853
- 8,007 ✅
- 8,254
- 8,421

**Solution: 8007**
```sql
SELECT COUNT(*)
FROM green_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```
Output:
```
8007
```

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

- 2025-11-14 ✅
- 2025-11-20
- 2025-11-23
- 2025-11-25

**Solution: 2025-11-14**

```sql
SELECT
  DATE(lpep_pickup_datetime) AS pickup_day,
  MAX(trip_distance) AS max_trip_distance
FROM green_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance < 100
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY max_trip_distance DESC
LIMIT 1;
```
Output:
```
pickup_day: 2025-11-14
max_trip_distance: 88.03
```

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- East Harlem North ✅
- East Harlem South
- Morningside Heights
- Forest Hills

**Solution: East Harlem North**
```sql
SELECT
  z."Zone" AS pickup_zone,
  SUM(t.total_amount) AS total_amount_sum
FROM green_trips t
JOIN zones z
  ON t."PULocationID" = z."LocationID"
WHERE t.lpep_pickup_datetime >= '2025-11-18'
  AND t.lpep_pickup_datetime <  '2025-11-19'
GROUP BY z."Zone"
ORDER BY total_amount_sum DESC
LIMIT 1;
```
Output:
```
pickup_zone: East Harlem North
total_amount_sum: 9281.919999999996
```

## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's `tip` , not `trip`. We need the name of the zone, not the ID.

- JFK Airport
- Yorkville West ✅
- East Harlem North
- LaGuardia Airport

**Solution: Yorkville West**

```sql
SELECT
  z_drop."Zone" AS dropoff_zone,
  t.tip_amount
FROM green_trips t
JOIN zones z_pick
  ON t."PULocationID" = z_pick."LocationID"
JOIN zones z_drop
  ON t."DOLocationID" = z_drop."LocationID"
WHERE z_pick."Zone" = 'East Harlem North'
  AND t.lpep_pickup_datetime >= '2025-11-01'
  AND t.lpep_pickup_datetime <  '2025-12-01'
ORDER BY t.tip_amount DESC
LIMIT 1;
```
Output:
```
dropoff_zone: Yorkville West
tip_amount: 81.89
```

## Terraform

In this section, Terraform was used to provision the required GCP infrastructure for the course. 

The Terraform configuration can be found in: `module-01-docker-terraform/terraform/gcp/`

This setup includes two main files:

- `main.tf`: defines the GCP resources, including:
  - a Google Cloud Storage bucket 
  - a BigQuery dataset
- `variables.tf`: declares configurable variables such as the GCP project ID, region, bucket name, and dataset name

The configuration was successfully applied in my GCP project using Terraform. After running `terraform apply`, both the GCS bucket and BigQuery dataset were created and verified in the GCP Console.  
The resources were later removed using `terraform destroy`.


## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy  ✅
- terraform import, terraform apply -y, terraform rm

**Solution Explanation:**
- `terraform init` initializes the working directory by downloading provider plugins and setting up the backend.
- `terraform apply -auto-approve` generates the execution plan and applies the changes without requiring manual approval.
- `terraform destroy` removes all infrastructure resources managed by Terraform.







