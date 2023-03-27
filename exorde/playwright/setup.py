from setuptools import find_packages, setup

setup(
    name="exorde_playwright",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["aiosow", "playwright", "playwright-stealth"],
)
