"""Pipeline to ingest NYC taxi data from the Data Engineering Zoomcamp API."""

import dlt
from dlt.sources.rest_api import rest_api_source


source = rest_api_source(
    {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/",
        },
        "resources": [
            {
                "name": "taxi_rides",
                "endpoint": {
                    "path": "data_engineering_zoomcamp_api",
                    "paginator": {
                        "type": "page_number",
                        "base_page": 1,
                        "page_param": "page",
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                },
                "write_disposition": "replace",
            },
        ],
    }
)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="nyc_taxi_data",
        dev_mode=True,
        progress="log",
    )
    load_info = pipeline.run(source)
    print(load_info)
