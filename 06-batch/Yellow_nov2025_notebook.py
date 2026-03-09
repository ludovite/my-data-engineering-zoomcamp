import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # from io import StringIO
    from pathlib import Path

    import pyspark
    from pyspark.sql import functions as F
    from pyspark.sql import SparkSession, types
    import requests

    return F, Path, SparkSession, requests, types


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🚀 Create a session
    """)
    return


@app.cell
def _(SparkSession):
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()
    return (spark,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🪛 Repartition Yellow taxi data from November 2025
    """)
    return


@app.cell
def _(Path):
    data_path = Path("data")
    data_file = "yellow_tripdata_2025-11"
    (data_path / "raw").mkdir(parents=True, exist_ok=True)
    (data_path / "parquet").mkdir(parents=True, exist_ok=True)
    return data_file, data_path


@app.cell
def _(data_file, data_path, spark):
    df = (
        spark
        .read.parquet(f"{data_path}/raw/{data_file}.parquet")
        .repartition(4)
    )
    df.write.parquet(f"{data_path}/parquet", mode="overwrite")
    return (df,)


@app.cell
def _(df):
    df.show()
    return


@app.cell
def _(df):
    df.createOrReplaceTempView("trips")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 👆 Count records on November, 15th
    """)
    return


@app.cell
def _(df):
    df.printSchema()
    return


@app.cell
def _(spark):
    spark.sql("""
    SELECT COUNT(tpep_pickup_datetime)
    FROM trips
    WHERE 
        DATE(tpep_pickup_datetime) >= '2025-11-15'
        AND DATE(tpep_pickup_datetime) < '2025-11-16'
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🕒 Longest trip
    """)
    return


@app.cell
def _(F, df):
    df_with_duration = (
        df
        .select("tpep_pickup_datetime", "tpep_dropoff_datetime")
        .withColumn("duration_hours",
                    F.timestamp_diff(
                        end="tpep_dropoff_datetime",
                        start="tpep_pickup_datetime",
                        unit="SECOND",
                    )
                    # convert seconds to hours
                    / 3_600.0
                   )
    )
    df_with_duration.show(5)

    max_duration = df_with_duration.agg(
        F.max("duration_hours")
    ).collect()[0][0]

    print(f"Longest duration: {max_duration:.1f} hours")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🖥️ User interface
    """)
    return


@app.cell
def _():
    print("""
    Spark UI is at http://localhost:4040
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🗺️ Least frequent pickup location zone
    """)
    return


@app.cell
def _():
    lookupdata_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    return (lookupdata_url,)


@app.cell
def _(Path, data_path, lookupdata_url, requests):
    lookupdata_file =  data_path / "raw" / Path(lookupdata_url.split("/")[-1])

    if not lookupdata_file.is_file():
        print(f"Downloading {lookupdata_url}…")
        response = requests.get(lookupdata_url, timeout=10)
        response.raise_for_status()
        lookupdata_file.write_text(response.text, encoding="utf-8")
        print(f"Writen to {lookupdata_file}")
    return (lookupdata_file,)


@app.cell
def _(lookupdata_file):
    str(lookupdata_file)
    return


@app.cell
def _(lookupdata_file, spark, types):
    schema_zones = types.StructType([
        types.StructField('LocationID', types.IntegerType(), True),
        types.StructField('Borough', types.StringType(), True),
        types.StructField('Zone', types.StringType(), True),
        types.StructField('service_zone', types.StringType(), True),
    ])

    df_zones = (
        spark.read
        .option("header", "true")
        .schema(schema_zones)
        .csv(str(lookupdata_file))
    )
    df_zones.show(5)
    return (df_zones,)


@app.cell
def _(df_zones):
    df_zones.printSchema()
    return


@app.cell
def _(df_zones):
    df_zones.createOrReplaceTempView("zones")
    return


@app.cell
def _(df):
    df.printSchema()
    return


@app.cell
def _(spark):
    spark.sql("""
    SELECT Zone, COUNT(PULocationID) AS freq
    FROM 
        trips AS tr
        INNER JOIN zones AS zo
            ON zo.LocationID = tr.PULocationID
    GROUP BY Zone
    ORDER BY freq ASC
    LIMIT 5
    """).show(truncate=False)
    return


if __name__ == "__main__":
    app.run()
