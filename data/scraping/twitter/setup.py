from setuptools import find_packages, setup

setup(
    name="a7df32de3a60dfdb7a0b",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "exorde_data",
        "aiohttp",
        "snscrape==0.6.2.20230320",
    ],
    extras_require={"dev": ["pytest", "pytest-cov", "pytest-asyncio"]},
)
