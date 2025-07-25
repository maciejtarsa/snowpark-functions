# snowpark-functions
Sample snowpark functions using Snowpark API

Documentation: https://docs.snowflake.com/en/developer-guide/snowflake-cli/snowpark/overview


## Steps
Initialise the project
```bash
snow init snowpark --template-source https://github.com/snowflakedb/snowflake-cli-templates --template example_snowpark
```
Follow the guide to provide some parameters.  

cd to the newly created folder
```bash
cd snowpark
```
Build the project
```bash
snow snowpark build
```
<p align="center">
  <img src="images/snowpark_build.png" alt="Result of building the project" />
</p>
Deploy the project

```bash
snow snowpark deploy --replace
```
<p align="center">
  <img src="images/snowpark_deploy.png" alt="Result of deploying the project" />
</p>
This will deploy the functions and procedures to your Snowflake environment using credentials from your `.snowflake/config.toml` file. Credentials and other parameters can also be provided with CLI flags.  

More information about Snowpark project definition: https://docs.snowflake.com/en/developer-guide/snowflake-cli/snowpark/create#label-snowcli-create-snowpark

### Snowpark scalar function

Functions can be defined very similarly to regular Python functions, e.g.:
```python
def hello_function(name: str) -> str:
    return f"Hello {name}
```
For the function to be pushed to Snowflake, you need to add it to `snowflake.yaml` file, e.g.:
```yaml
entities:
  hello_function:
    type: function
    identifier:
      name: hello_function
    handler: python_package.functions.hello_function
    signature:
      - name: name
        type: string
    returns: string
    meta:
      use_mixins:
        - snowpark_shared
```
### Snowpark table functions

Table functions (or UDTFs) are a special type of functions that return a single value per input value - in other words - they take a table and return a table with some transformations applied for each row.

Defining them with Python is slightly more complicated though, as they require a class with `process()` function that yields results, e.g.
```python
class TransformTable:
    def process(self, id, value):
        # processes each input row
        yield (id, f"Hello {value}!")
```
Sample definition in `snowflake.yaml` file, e.g.:
```yaml
  transform_table:
    type: function
    identifier:
      name: transform_table
    handler: python_package.table_functions.TransformTable
    signature:
      - name: id
        type: string
      - name: value
        type: string
    returns: TABLE (id VARCHAR, new_value VARCHAR)
    meta:
      use_mixins:
        - snowpark_shared
```
This definitition is also more compes as it requires definition of input parameters (rows in your input table and their types) and output parameters and types.  

More information on defining these: https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-tabular-functions

## Execution

### Local

To execute the function locally
```bash
snow snowpark execute function "hello_function('Olaf')"
```

<p align="center">
  <img src="images/snowpark_execute.png" alt="Result of executing a function" />
</p>

### Examples and dbt models

Once deployed, they can be used in your Snowflake SQL oe Python code.  
Scalar functions:
```sql
select
    id,
    dbt_demo.custom_functions.hello_function(name) as augmented_name,
from source_data
```
```python
result_df = source_df.select(
      "id",
      session.call_function("dbt_demo.custom_functions.hello_function", source_df["name"]).alias("augmented_name")
  )
```
And table functions:
```sql
SELECT transform_table.id, transform_table.new_value
  FROM source_data, TABLE(dbt_demo.custom_functions.transform_table(id, value));
```
```python
sql = 
result_df = session.sql(
  f"""
    SELECT t.id, t.value
    FROM {input_df} t,
    TABLE(dbt_demo.custom_functions.transform_table(t.id, t.value))
"""
)
```

Sample dbt models for functions and table functions can be found in `sample_dbt_models` directory.

---

## Snowpark packages

While the above deploys the code as functions and stored procedures in Snowflake, there is an alternative way to deploy them as packages or individual Python files.

### Individual Python files

Indovidual Python files can be deployed to Snowflake stages and then accessed in Python code.

For example, to deploy a single Python file
```bash
cd snowpark/python_package
snow snowpark package upload --file="sample_function.py" --stage="packages" --overwrite --schema dev
```
That file can be be added to imports in your dbt Python model and used with
```python
from snowflake.snowpark.custom_functions import lit
def model(dbt, session):
    dbt.config(
        materialized = "table",
        imports = ['@dbt_demo.custom_functions.packages/sample_function.py'],
    )
    import sample_function
    source_df = dbt.ref("raw_table")  
    final_df = source_df.withColumn("CHECK", lit(sample_function.print_hello("Alice")))
    return final_df
```

### Python packages

First, we need to zip the code as a package. Ensure that you have `__init__.py` files in any folders
```bash
cd snowpark
zip -r python_package.zip python_package
cd ..
```
You can also achieve this with running snow command `snow snowpark build` if using snowpark setup mentioned above.  
The package can then be uploaded to Snowflake
```bash
snow snowpark package upload --file="python_package.zip" --stage="packages" --overwrite --schema dev
```

That package can be be added to imports in your dbt Python model. Note - it needs to be zipped with the folder and Python files inside this folder. When Snowflake unpacks it - it will refer to that folder name as the package name.
```python
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
```

## Permissions

Storing these functions and packages in a database and schema accessible from across the acount would be advisable.
```sql
CREATE SCHEMA dbt_demo.custom_functions;
CREATE STAGE dbt_demo.custom_functions.packages;
```

In order to access these functions and packages, users needing access would require the following permissions:
```sql
GRANT USAGE ON DATABASE dbt_demo TO ROLE my_role;
GRANT USAGE ON SCHEMA dbt_demo.custom_functions TO ROLE my_role;
GRANT USAGE, READ ON STAGE dbt_demo.custom_functions.packages TO ROLE my_role;
GRANT USAGE ON FUTURE FUNCTIONS IN SCHEMA dbt_demo.custom_functions TO ROLE my_role;
GRANT USAGE ON FUTURE PROCEDURES IN SCHEMA dbt_demo.custom_functions TO ROLE my_role;
```
We're using future functions/procedures here so that users have access to any functions created in the future.
It may be a good idea to also create a specific role that will have permission to create functions/procedures and upload packages to Snowflake.

## Testing

Thorough testing is essential to ensure your Snowpark functions behave as expected before deployment.

### Local testing
Local testing is useful for quick debugging and validation during development. To enable this, include a __main__ block in your Python file:
```python
# For local debugging
# Be aware you may need to type-convert arguments if you add input parameters
if __name__ == "__main__":
    print(hello_function(*sys.argv[1:]))  # type: ignore
```
Run the script with:
```bash
python3 snowpark/python_package/functions.py Jane
```
### pytest
For more robust and repeatable testing, use Pytest. This allows you to define unit tests and run them automatically.  
Example test file: `python_packages/tests/test_functions.py`
```python
import pytest
from python_package.functions import hello_function
def test_hello_function():
    assert hello_function("World") == "Hello World!"
    assert hello_function("Alice") == "Hello Alice!"
    assert hello_function("") == "Hello !"
```
Run all tests with:
```bash
pytest snowpark_functions
```
More info: [Snowflake documentation](https://docs.snowflake.com/en/developer-guide/snowpark/python/testing-python-snowpark)
