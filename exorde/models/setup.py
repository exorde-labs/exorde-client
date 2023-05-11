from setuptools import find_packages, setup

setup(
    name="exorde_models",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["jschemator", "aiosow"],
)
