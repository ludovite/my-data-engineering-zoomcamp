with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        dispatching_base_num as dispatching_base_num,
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropOff_datetime as timestamp) as dropoff_datetime,
        cast(PUlocationid as integer) as pickup_location_id,
        cast(DOlocationid as integer) as dropoff_location_id,
        SR_flag as sr_flag,
        Affiliated_base_number as affiliated_base_number
    from source
    -- Filter out records with null dispatching_base_num 
    where dispatching_base_num is not null
)

select * from renamed

-- Sample records for dev environment using deterministic date filter
{% if target.name == 'dev' %}
where pickup_datetime >= '2019-01-01' and pickup_datetime < '2019-02-01'
{% endif %}
