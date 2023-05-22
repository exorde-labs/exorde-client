"""Test wether packages respect the defined interface."""
import pytest, inspect, importlib

from .utils import discover_packages


@pytest.mark.parametrize("package_name", discover_packages("./scraping"))
def test_package_functions(package_name):
    (name, alias) = package_name
    module = importlib.import_module(alias)
    assert "query" in dir(
        module
    ), f"`query` is absent from the `{name}` package"

    query_signature = inspect.signature(module.query)
    assert any(
        param.default == inspect.Parameter.empty
        and param.kind == param.POSITIONAL_OR_KEYWORD
        for param in query_signature.parameters.values()
    ), "f`{name}.query` should take a positonal argument"

    assert inspect.isasyncgenfunction(
        module.query
    ), f"`{name}.query` should be an async-generator"
