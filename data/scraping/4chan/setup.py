from setuptools import find_packages, setup

setup(
    name="ch4875eda56be56000ac",
    version="0.0.2",
    packages=find_packages(),
    install_requires=["lxml", "exorde_data", "aiohttp", "flashtext", "HTMLParser"],
    extras_require={"dev": ["pytest", "pytest-cov", "pytest-asyncio"]},
)
