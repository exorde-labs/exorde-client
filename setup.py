from setuptools import find_packages, setup

setup(
    name="exorde_data",
    version="0.0.5",
    packages=find_packages(include=["exorde_data"]),
    install_requires=["madtypes"],
    entry_points={
        "console_scripts": ["exorde_data = exorde_data.__init__:print_schema"]
    },
)
