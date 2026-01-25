#!/usr/bin/env python
# coding: utf-8

import click


import pandas as pd
from sqlalchemy import create_engine


# Default values
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5433
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "ny_taxi"
POSTGRES_TABLE = "green_taxi_data"
TRIPS_FILE = "green_tripdata_2025-11.parquet"
ZONES_FILE = "taxi_zone_lookup.csv"

# Command Line Interface with `click`


@click.command()
@click.option("--pg-user", default=POSTGRES_USER, help="PostgreSQL user")
@click.option("--pg-passwd", default=POSTGRES_PASSWORD, help="PostgreSQL password")
@click.option("--pg-host", default=POSTGRES_HOST, help="PostgreSQL host")
@click.option("--pg-port", default=POSTGRES_PORT, type=int, help="PostgreSQL port")
@click.option("--pg-db", default=POSTGRES_DB, help="PostgreSQL database name")
# @click.option('--year', default=2025, type=int, help='Year of the data')
# @click.option('--month', default=11, type=int, help='Month of the data')
@click.option("--target-table", default=POSTGRES_TABLE, help="Target table name")
def run(pg_user, pg_passwd, pg_host, pg_port, pg_db, target_table):
    """
    Ingest NYC taxi data (used by homework ##1) into PostgreSQL database.
    """

    df = (
        pd.read_parquet(TRIPS_FILE)
        .drop(columns="ehail_fee")  # full of NaN values
        .astype(
            {
                "RatecodeID": "Int64",
                "passenger_count": "Int64",
                "payment_type": "Int64",
                "trip_type": "Int64",
                "VendorID": "Int64",
                "PULocationID": "Int64",
                "DOLocationID": "Int64",
                # cbd_congestion_fee → new
            }
        )
    )

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_passwd}@{pg_host}:{pg_port}/{pg_db}"
    )

    df.head(n=0).to_sql(
        name=target_table,
        con=engine,
        if_exists="replace",
    )
    print("Table created")
    df.to_sql(
        name=target_table,
        con=engine,
        if_exists="append",
    )
    print("Table completed\n")

    df = pd.read_csv("taxi_zone_lookup.csv")

    df.head(n=0).to_sql(
        name=ZONES_FILE[:-4],
        con=engine,
        if_exists="replace",
    )
    print("Table created")
    df.to_sql(
        name=ZONES_FILE[:-4],
        con=engine,
        if_exists="append",
    )
    print("Table completed\n")


if __name__ == "__main__":
    run()
