from snowflake.snowpark.functions import lit

def model(dbt, session):
    dbt.config(
        materialized = "table",
        imports = ['@dbt_demo.custom_functions.packages/sample_function.py'],
    )
    import sample_function
    source_df = dbt.ref("raw_table")  
    final_df = source_df.withColumn("CHECK", lit(sample_function.print_hello("Alice")))
    return final_df
