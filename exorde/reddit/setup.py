from setuptools import find_packages, setup

setup(
    name="exorde_reddit",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["aiosow", "lxml", "exorde_schema", "aiohttp"],
    extras_require={"dev": ["pytest", "pytest-cov", "pytest-asyncio"]},
)
