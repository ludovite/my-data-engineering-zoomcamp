# Module 1 Homework: Docker & SQL

In this homework we prepare the environment and practice
Docker and SQL


## Part 1. Understanding Docker images

To run docker with the `python:3.13` image and an entrypoint `bash` to interact with the container:

```bash
$ docker run -it --rm python:3.13 bash -c 'pip --version'
pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

This Docker image has version 25.3 of `pip`


## Part 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`:

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

To connect/register to the postgres database,
pgadmin should use the `hostname` and `port` like this:
`db:5432`


## Prepare the Data

Now, let’s download the green taxi trips data for November 2025
and the dataset with zones:

```bash
$ wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
$ wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

After launching the database server with the command: `docker-compose up`, these two data file are put inside SQL tables: `uv run python data-ingest.py`.

Connecting to pgAdmin at `localhost:8080`, SQL requests help to resolve the following parts.


## Part 3. Counting short trips

```sql
SELECT COUNT(*)
FROM green_taxi_data
WHERE 
	lpep_pickup_datetime >= TIMESTAMP '2025-11-01'
	AND
	lpep_pickup_datetime <  TIMESTAMP '2025-12-01'
	AND
	trip_distance <= 1
;
```

In November 2025, **8,007 trips** had a `trip_distance` of less than or equal to 1 mile.


## Part 4. Longest trip for each day

```sql
SELECT DATE(lpep_pickup_datetime), trip_distance
FROM green_taxi_data
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1
;
```

The pick up day with the longest trip distance (88 miles) is **2025-11-14**.
NB: I only considered trips with `trip_distance` less than 100 miles (to exclude data errors).


## Part 5. Biggest pickup zone

```sql
SELECT zones."Zone", SUM(total_amount) AS "Total_Amounts"
FROM green_taxi_data AS trips
	INNER JOIN taxi_zone_lookup AS zones
		ON zones."LocationID" = trips."PULocationID"
WHERE 
	lpep_pickup_datetime >= TIMESTAMP '2025-11-18'
	AND
	lpep_pickup_datetime < TIMESTAMP '2025-11-19'
GROUP BY zones."Zone"
ORDER BY "Total_Amounts" DESC
LIMIT 1
;
```

The pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025 is **East Harlem North**.


## Question 6. Largest tip

```sql
SELECT (
	SELECT "Zone" FROM taxi_zone_lookup
	WHERE "LocationID" = trips."DOLocationID"
	) AS "Drop off zone"
FROM green_taxi_data AS trips
WHERE
	"PULocationID" = (
		SELECT "LocationID" FROM taxi_zone_lookup
		WHERE "Zone" = 'East Harlem North'
	)
ORDER BY tip_amount DESC
LIMIT 1
;
```

For the passengers picked up in the zone named "East Harlem North" in November 2025, **Yorkville West** was the drop off zone that had the largest tip.


## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform.
Copy the files from the course repo
[here](../../../01-docker-terraform/terraform/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw1


## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

### Why learn in public?

- Accountability: Sharing your progress creates commitment and motivation to continue
- Feedback: The community can provide valuable suggestions and corrections
- Networking: You'll connect with like-minded people and potential collaborators
- Documentation: Your posts become a learning journal you can reference later
- Opportunities: Employers and clients often discover talent through public learning

You can read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

Don't worry about being perfect. Everyone starts somewhere, and people love following genuine learning journeys!

### Example post for LinkedIn

```
🚀 Week 1 of Data Engineering Zoomcamp by @DataTalksClub complete!

Just finished Module 1 - Docker & Terraform. Learned how to:

✅ Containerize applications with Docker and Docker Compose
✅ Set up PostgreSQL databases and write SQL queries
✅ Build data pipelines to ingest NYC taxi data
✅ Provision cloud infrastructure with Terraform

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X


```
🐳 Module 1 of Data Engineering Zoomcamp done!

- Docker containers
- Postgres & SQL
- Terraform & GCP
- NYC taxi data pipeline

My solution: <LINK>

Free course by @DataTalksClub: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```


