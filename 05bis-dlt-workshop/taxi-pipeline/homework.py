import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md("# NYC Taxi Data - Homework")
    return (mo,)


@app.cell
def _():
    import dlt
    import ibis

    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="nyc_taxi_data",
    )
    # Get an ibis connection from the dlt dataset
    dataset = pipeline.dataset()
    con = dataset.ibis()
    rides = con.table("taxi_rides")
    return (rides,)


@app.cell
def _(mo, rides):
    start = rides.trip_pickup_date_time.min().execute()
    end = rides.trip_dropoff_date_time.max().execute()
    mo.md(
        f"""
        ## Question 1: Date range of the dataset

        | | Date |
        |---|---|
        | **Start date** | `{start}` |
        | **End date** | `{end}` |
        """
    )
    return


@app.cell
def _(mo, rides):
    total_trips = rides.count().execute()
    credit_trips = rides.filter(rides.payment_type.lower() == "credit").count().execute()
    proportion = round(credit_trips / total_trips * 100, 2)
    mo.md(
        f"""
        ## Question 2: Proportion of trips paid with credit card

        | Metric | Value |
        |---|---|
        | Total trips | `{total_trips}` |
        | Credit card trips | `{credit_trips}` |
        | **Proportion** | **`{proportion}%`** |
        """
    )
    return


@app.cell
def _(mo, rides):
    total_tips = round(rides.tip_amt.sum().execute(), 2)
    mo.md(
        f"""
        ## Question 3: Total tips generated

        **Total tips: `${total_tips:,.2f}`**
        """
    )
    return


if __name__ == "__main__":
    app.run()
