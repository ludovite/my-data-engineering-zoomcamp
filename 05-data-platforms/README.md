# Module 5: Data Platforms with Bruin

In this homework, we used Bruin to build a complete NYC taxi data pipeline, from ingestion to reporting.

## Setup. Bruin poipeline with AI-assisted Workflow

For the best learning experience, I considered a hybrid approach where I did the initial setup myself, then let AI help with more complex parts, as described in this [tutoriel](https://github.com/bruin-data/bruin/tree/main/templates/zoomcamp#45-ai-assisted-workflow).

1. **I did**: Install CLI, run `bruin init`, explore the generated files
2. **AI helps**: Configure connections, explain materialization strategies
3. **I did**: Create a first simple asset (e.g., the seed CSV)
4. **AI helps**: Build the Python ingestion and complex SQL transformations
5. **I did**: Run and validate, inspect the data
6. **AI helps**: Debug issues, add quality checks, optimize

---

### Question 1. Bruin Pipeline Structure

In a Bruin project, what are the required files/directories?

- **`.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`**

```
├── .bruin.yml
├── .gitignore
├── README.md
└── pipeline
    ├── pipeline.yml
    └── assets
        ├── ingestion
        │   ├── payment_lookup.asset.yml
        │   ├── payment_lookup.csv
        │   ├── requirements.txt
        │   ├── trips.py
        │   └── __pycache__
        │       └── trips.cpython-311.pyc
        ├── reports
        │   └── trips_report.sql
        └── staging
            └── trips.sql
```
---

### Question 2. Materialization Strategies

Building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?

- **`time_interval` − incremental based on a time column.**

---

### Question 3. Pipeline Variables

Here is the following variable defined in `pipeline.yml`:

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

How to override variable this when running the pipeline to only process yellow taxis?

- **`bruin run --var 'taxi_types=["yellow"]'`**

---

### Question 4. Running with Dependencies

You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

- **`bruin run ingestion/trips.py --downstream`**

---

### Question 5. Quality Checks

You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

- **`name: not_null`**

---

### Question 6. Lineage and Dependencies

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- **`bruin lineage`**

---

### Question 7. First-Time Run

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- **`--full-refresh`**

---

