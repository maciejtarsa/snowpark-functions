with source_data as (
    select id, value
    from {{ ref('raw_my_table') }}
)

SELECT transform_table.id, transform_table.new_value
  FROM source_data, TABLE(DBT_DEMO.DEV.transform_table(id, value));
