import pytest
from python_package.functions import hello_function
def test_hello_function():
    assert hello_function("World") == "Hello World!"
    assert hello_function("Alice") == "Hello Alice!"
    assert hello_function("") == "Hello !"
