with source_data as (
    select *
    from {{ ref('raw_table') }}
)

select
    id,
    dev.hello_function(name) as augmented_name,
from source_data