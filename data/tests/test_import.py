"""Test wether packages are importable"""

import pytest

from .utils import discover_packages
import exorde_data


@pytest.mark.parametrize("package_name", discover_packages("./scraping"))
def test_package_importation(package_name):
    (name, __alias__) = package_name
    assert name in dir(exorde_data.scraping)
