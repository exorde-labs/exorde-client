"""Test wether packages respect the unified interface."""
import pytest, os, re, inspect
import importlib


def get_package_name(setup_file_path):
    # Read the setup.py file as text
    with open(setup_file_path, "r") as file:
        content = file.read()

    # Use regular expressions to extract the package name
    package_name_match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if package_name_match:
        package_name = package_name_match.group(1)
    else:
        raise ValueError("Package name not found in setup.py.")

    return package_name


def discover_packages(folder_path):
    result = []
    folders = os.listdir(folder_path)
    for folder in folders:
        setup_file = os.path.abspath(
            os.path.join("scraping/" + folder, "setup.py")
        )
        print(folder)
        package_name = get_package_name(setup_file)
        result.append((folder, package_name))
    return result


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
        module.query("test")
    ), f"`{name}.query` should return an async-generator"
