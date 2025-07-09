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
This will deploy the functions to your Snowflake environment using credentials from your `.snowalake/config.toml` file. Credentials and other parameters can also be provided with CLI flags.  

More information about Snowpark project definition: https://docs.snowflake.com/en/developer-guide/snowflake-cli/snowpark/create#label-snowcli-create-snowpark

## Functions

### Snowpark function

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
    handler: functions.hello_function
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
    handler: table_functions.TransformTable
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

### dbt models

Sample dbt models for functions and table functions can be found in `sample_dbt_models` directory.

## Testing

Functions can be tested locally if they contain main block for local testing/debugging, e.g.
```python
# For local debugging
# Be aware you may need to type-convert arguments if you add input parameters
if __name__ == "__main__":
    print(hello_function(*sys.argv[1:]))  # type: ignore
```
This can be tested by running
```bash
python3 snowpark/app/functions.py Jane
```
Pytest can also be used, more info in [Snowflake documentation](https://docs.snowflake.com/en/developer-guide/snowpark/python/testing-python-snowpark)
