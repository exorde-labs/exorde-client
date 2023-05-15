from setuptools import find_packages, setup

setup(
    name="exorde_models",
    version="0.0.1",
    packages=find_packages(include="exorde_models"),
    install_requires=["jschemator", "aiosow"],
    entry_points={
        "console_scripts": [
            "exorde_models = exorde_models.__init__:print_schema"
        ]
    },
)
