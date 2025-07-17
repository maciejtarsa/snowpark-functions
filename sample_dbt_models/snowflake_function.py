def model(dbt, session):
    # Configure the model materialization
    dbt.config(materialized="table")

    # Reference upstream dbt model or source
    source_df = dbt.ref("raw_table")  # or dbt.source("my_source", "raw_table")

    # Use Snowpark DataFrame API to select columns and apply the scalar function
    result_df = source_df.select(
        "id",
        session.call_function("dbt_demo.custom_functions.hello_function", source_df["name"]).alias("augmented_name")
    )

    return result_df