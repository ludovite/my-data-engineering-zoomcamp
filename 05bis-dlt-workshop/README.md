# Homework: Build My Own dlt Pipeline

We've seen how to build a pipeline with a scaffolded source. Now it's your turn to do it from scratch with a **custom API**.

## Workshop Content

* [Workshop README](README.md)
* [dlt Pipeline Overview Notebook (Google Colab)](https://colab.research.google.com/github/anair123/data-engineering-zoomcamp/blob/workshop/dlt_2026/cohorts/2026/workshops/dlt/dlt_Pipeline_Overview.ipynb)
* [Workshop registration page](https://luma.com/hzis1yzp)

## The Challenge

For this homework, build a dlt pipeline that loads NYC taxi trip data from a custom API into DuckDB and then answer some questions using the loaded data.

## Data Source

You'll be working with **NYC Yellow Taxi trip data** from a custom API (not available as a dlt scaffold). This dataset contains records of individual taxi trips in New York City.

| Property | Value |
|----------|-------|
| Base URL | `https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api` |
| Format | Paginated JSON |
| Page Size | 1,000 records per page |
| Pagination | Stop when an empty page is returned |

## Setup Instructions

Since this API is custom (not one of the scaffolds in dlt workspace), the setup is slightly different.

### Step 1: Create a New Project (or Reuse Your Demo Project)

If you already created a project folder while following along with the workshop demo, you can reuse that folder. Otherwise, create a new one:

```bash
mkdir taxi-pipeline
cd taxi-pipeline
```

Open this folder in Cursor (or your preferred agentic IDE).

### Step 2: Set Up the dlt MCP Server (If Not Already Done)

Choose the setup for your IDE:

Cursor - go to **Settings → Tools & MCP → New MCP Server** and add:

```json
{
  "mcpServers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "dlt[duckdb]",
        "--with",
        "dlt-mcp[search]",
        "python",
        "-m",
        "dlt_mcp"
      ]
    }
  }
}
```

VS Code (Copilot) - create `.vscode/mcp.json` in your project folder:

```json
{
  "servers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "dlt[duckdb]",
        "--with",
        "dlt-mcp[search]",
        "python",
        "-m",
        "dlt_mcp"
      ]
    }
  }
}
```

Claude Code - run in your terminal:

```bash
claude mcp add dlt -- uv run --with "dlt[duckdb]" --with "dlt-mcp[search]" python -m dlt_mcp
```

This enables the dlt MCP server, giving the AI access to dlt documentation, code examples, and your pipeline metadata.

### Step 3: Install dlt

```bash
uv add 'dlt[workspace]'
```

### Step 4: Initialize the Project

```bash
dlt init dlthub:taxi_pipeline duckdb
```

You can name the project whatever you like. Since this API has no scaffold, the command will create:
- The dlt project files
- Cursor rules for AI assistance

**But no YAML file with API metadata.** You will need to provide the API information yourself.

### Step 5: Prompt the Agent

Now use your AI assistant to build the pipeline. You'll need to provide the API details in your prompt since there's no scaffold.

Here's an example to get you started:

```
Build a REST API source for NYC taxi data.

API details:
- Base URL: https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api
- Data format: Paginated JSON (1,000 records per page)
- Pagination: Stop when an empty page is returned

Place the code in taxi_pipeline.py and name the pipeline taxi_pipeline.
Use @dlt rest api as a tutorial.
```

### Step 6: Run and Debug

Run your pipeline and iterate with the agent until it works:

```bash
uv run python taxi_pipeline.py
```

---

## Questions

Once your pipeline has run successfully, use the methods covered in the workshop to investigate the following:

- **dlt Dashboard**: `dlt pipeline taxi_pipeline show`
- **dlt MCP Server**: Ask the agent questions about your pipeline
- **Marimo Notebook**: Build visualizations and run queries

We challenge you to try out the different methods explored in the workshop when answering these questions to see what works best for you. Feel free to share your thoughts on what worked (or didn't) in your submission!

### Question 1: What is the start date and end date of the dataset?

- Querying the db with **duckdb ui** or with the **dlt dashboard**:
```sql
SELECT
  MIN(DATE(trip_pickup_date_time)) AS 'Start date',
  MAX(DATE(trip_dropoff_date_time)) AS 'End date'
FROM "taxi_rides"
;
```

- Asking the same question to Claude Code, the AI agent tries to answer with this command:
```bash
dlt - execute_sql_query(pipeline_name: "taxi_pipeline", sql_select_query: "SELECT
   MIN(trip_pickup_date_time) as start_date, MAX(trip_pickup_date_time) as end_date FROM
   taxi_rides") (MCP)
```
We could suggest Claude to analyse the column `trip_dropoff_date_time` about the end date.

Answer: **2009-06-01 to 2009-07-01**

### Question 2: What proportion of trips are paid with credit card?

```sql
WITH credit_trips AS (
  SELECT COUNT(payment_type) AS total
  FROM taxi_rides
  WHERE payment_type ILIKE 'credit'
  )

SELECT credit_trips.total AS credit_trips
  , COUNT(*) AS total_trips
  , ROUND(credit_trips.total * 100.0 / COUNT(*), 2) AS credit_pct
FROM taxi_rides, credit_trips
GROUP BY credit_trips.total;
```

Answer: **26.66%**

### Question 3: What is the total amount of money generated in tips?

```sql
SELECT ROUND(SUM(tip_amt), 2) AS total_tips
FROM taxi_rides;
```

Answer: **$6,063.41**

---

### Annex: Asking Claude Code to find the answers and reporting in a marimo notebook

Prompt:
```txt
❯ Create a marimo notebook that gives an answer to these questions:
  1. What is the start date and end date of the dataset?
  2. What proportion of trips are paid with credit card?
  3. What is the total amount of money generated in tips?
  Use ibis for data access.
  Reference: https://dlthub.com/docs/general-usage/dataset-access/marimo
```

Notes: Because the db schema has the dev_mode timestamp suffix, Claude code had to re-run the pipeline without dev_mode first to get a clean schema name.
Then it could correct a few bugs from its first attempts. I asked it to get back to a dev pipeline.

Results: the generated marimo file is [here](./homework.py). Inside the chat window, this results table was printed:
```
● Done. The marimo notebook is at homework.py. Here are the verified answers:

  ┌───────────────────────────┬──────────────────────────┐
  │         Question          │          Answer          │
  ├───────────────────────────┼──────────────────────────┤
  │ Q1 Date range             │ 2009-06-01 to 2009-07-01 │
  ├───────────────────────────┼──────────────────────────┤
  │ Q2 Credit card proportion │ 26.66%                   │
  ├───────────────────────────┼──────────────────────────┤
  │ Q3 Total tips             │ $6,063.41                │
  └───────────────────────────┴──────────────────────────┘

  Run the notebook with:
  marimo edit homework.py
```

---

### Resources

| Resource | Link |
|----------|------|
| dlt Dashboard Docs | [dlthub.com/docs/general-usage/dashboard](https://dlthub.com/docs/general-usage/dashboard) |
| marimo + dlt Guide | [dlthub.com/docs/general-usage/dataset-access/marimo](https://dlthub.com/docs/general-usage/dataset-access/marimo) |
| dlt Documentation | [dlthub.com/docs](https://dlthub.com/docs) |

---
