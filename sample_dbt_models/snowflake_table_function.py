def model(dbt, session):
    # Configure materialization
    dbt.config(materialized="table")

    # Reference upstream dbt model or source
    input_df = dbt.ref("raw_my_table")

    # Call the Snowpark Python table function with the input dataframe as a subquery
    sql = f"""
        SELECT t.id, t.value
        FROM {input_df} t,
        TABLE(dbt_demo.custom_functions.transform_table(t.id, t.value))
    """

    # Execute the query and return the result as a Snowpark DataFrame
    result_df = session.sql(sql)

    return result_df