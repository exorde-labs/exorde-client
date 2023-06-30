from setuptools import find_packages, setup

setup(
    name="ap98j3envoubi3fco1kc",
    version="0.0.6",
    packages=find_packages(),
    install_requires=["lxml", "exorde_data", "aiohttp"],
    extras_require={"dev": ["pytest", "pytest-cov", "pytest-asyncio"]},
)
