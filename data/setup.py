from setuptools import find_packages, setup

setup(
    name="exorde_data",
    version="0.0.1",
    packages=find_packages(include="exorde_data"),
    install_requires=["jdatator", "aiosow"],
    entry_points={
        "console_scripts": ["exorde_data = exorde_data.__init__:print_schema"]
    },
)
