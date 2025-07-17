from snowflake.snowpark.functions import lit

def model(dbt, session):

    dbt.config(
        materialized = "table",
        imports = ['@dbt_demo.custom_functions.packages/python_package.zip'],
    )

    from python_package import functions
    functions.hello_function('name')

    # Get tables using dbt's ref function to reference the raw_pos models
    locations_df = dbt.ref('raw_pos_location')
    final_df = (
        locations_df.withColumn("CHECK", lit(functions.hello_function("Mirian")))
    )
    
    return final_df