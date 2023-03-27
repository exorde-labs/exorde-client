from setuptools import find_packages, setup

setup(
    name="exorde_protocol",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["aiosow", "python-dateutil", "pyyaml", "web3"],
)
