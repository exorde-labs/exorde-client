from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="exorde",
    version="0.1.1",
    description="Exorde CLI",
    packages=find_packages(
        include=["exorde", "exorde.protocol.*", "exorde.drivers"]
    ),
    include_package_data=True,
    license="MIT",
    entry_points={
        "console_scripts": [
            "exorde = exorde.__init__:launch",
            "exorde_protocol_schema = exorde.protocol:print_schema",
        ],
    },
    install_requires=["web3", "exorde_lab", "aiosow", "aiohttp"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires="==3.10.*",
)
