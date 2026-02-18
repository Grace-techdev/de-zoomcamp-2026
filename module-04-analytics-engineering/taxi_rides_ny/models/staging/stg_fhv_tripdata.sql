with source as (

    select *
    from {{ source('raw', 'fhv_tripdata') }}

),

renamed as (

    select
        -- identifiers
        cast(dispatching_base_num as string) as dispatching_base_num,

        -- timestamps
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropoff_datetime as timestamp) as dropoff_datetime,

        -- location ids
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,

        -- sr flag
        cast(sr_flag as integer) as sr_flag

    from source

    -- homework requirement
    where dispatching_base_num is not null

)

select * from renamed

{% if target.name == 'dev' %}
where pickup_datetime >= '2019-01-01'
  and pickup_datetime < '2019-02-01'
{% endif %}