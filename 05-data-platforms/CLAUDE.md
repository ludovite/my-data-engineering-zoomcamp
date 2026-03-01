# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Module 5 of the Data Engineering Zoomcamp. Build a complete NYC Taxi ELT pipeline using **Bruin** — a unified CLI tool for data ingestion, transformation, orchestration, and quality checks.

The Bruin MCP server is configured for this project (`claude mcp add bruin -- bruin mcp`), giving access to Bruin docs and command execution directly.

## Common Commands

```bash
# Validate pipeline (fast — catches errors before running)
bruin validate ./zoomcamp/pipeline/pipeline.yml --environment default

# Run full pipeline (first time: use --full-refresh to create tables from scratch)
bruin run ./zoomcamp/pipeline/pipeline.yml --environment default --full-refresh

# Run a single asset + all downstream dependencies
bruin run ./zoomcamp/pipeline/assets/ingestion/trips.py \
  --environment default \
  --start-date 2022-01-01 --end-date 2022-02-01 \
  --var 'taxi_types=["yellow"]' \
  --downstream

# Run quality checks only
bruin run ./zoomcamp/pipeline/pipeline.yml --only checks

# Query a table
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"

# View asset lineage
bruin lineage ./zoomcamp/pipeline/assets/ingestion/trips.py

# Test connection
bruin connections ping duckdb-default
```

## Pipeline Architecture

Three-layer ELT pipeline under `zoomcamp/pipeline/assets/`:

```
ingestion/
  trips.py                # Python asset — fetches NYC TLC parquet files month-by-month
  payment_lookup.asset.yml + payment_lookup.csv  # Seed asset — static CSV lookup table
staging/
  trips.sql               # Cleans, deduplicates (ROW_NUMBER), enriches via JOIN with payment_lookup
reports/
  trips_report.sql        # Aggregates staging data by date/taxi_type/payment_type
```

**Data flow:** `ingestion.trips` + `ingestion.payment_lookup` → `staging.trips` → `reports.trips_report`

## Key Configuration Files

- **`.bruin.yml`** (project root, gitignored): Environments and connection credentials. Must be present but never committed.
- **`pipeline/pipeline.yml`**: Pipeline name, schedule, `start_date`, `default_connections`, and the `taxi_types` variable (array of strings, e.g. `["yellow", "green"]`).

## Asset Patterns

### Python assets (`trips.py`)
- Metadata block delimited by `"""@bruin` ... `@bruin"""`
- Implement `materialize()` to return a DataFrame; Bruin loads it into the destination
- Read date window from env vars `BRUIN_START_DATE` / `BRUIN_END_DATE`
- Read pipeline variables from `BRUIN_VARS` (JSON string)
- Dependencies listed in `requirements.txt` next to the asset

### SQL assets (`.sql`)
- Metadata block delimited by `/* @bruin` ... `@bruin */`
- Use Jinja variables `{{ start_datetime }}` / `{{ end_datetime }}` in WHERE clause when using `time_interval` strategy (required to avoid duplicates)
- Declare `depends:` to establish DAG ordering and enable `--downstream`

### Seed assets (`.asset.yml`)
- Type `duckdb.seed` with `parameters.path` pointing to a CSV file

## Materialization Strategies

| Strategy | Used in | Behavior |
|---|---|---|
| `append` | ingestion | Insert-only; duplicates handled downstream |
| `time_interval` | staging, reports | Deletes rows in run window, re-inserts query results |

For `time_interval`: always use the same `incremental_key` (`pickup_datetime`) across staging and reports layers.

## Data Source

NYC TLC parquet files: `https://d37ci6vzurychx.cloudfront.net/trip-data/<taxi_type>_tripdata_<YYYY>-<MM>.parquet`

Data availability ends **November 2025**. Use 1-3 months for development; run full backfill only after pipeline is validated.

## Deployment (Cloud)

To switch from DuckDB to BigQuery:
1. Add a `google_cloud_platform` connection to `.bruin.yml`
2. Change `default_connections.duckdb` → `default_connections.bigquery` in `pipeline.yml`
3. Change asset types: `duckdb.sql` → `bq.sql`, `duckdb.seed` → `bq.seed`
4. Fix SQL dialect differences (types, functions)
