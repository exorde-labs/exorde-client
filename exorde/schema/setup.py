from setuptools import find_packages, setup

setup(
    name="exorde_schema",
    version="0.0.1",
    packages=find_packages(include="exorde_schema"),
    install_requires=["jschemator", "aiosow"],
    entry_points={
        "console_scripts": [
            "exorde_schema = exorde_schema.__init__:print_schema"
        ]
    },
)
