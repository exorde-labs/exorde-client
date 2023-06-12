from setuptools import find_packages, setup

setup(
    name="exorde",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "madtypes",
        "pyyaml",
        "eth-account",
        "asyncio",
        "aiohttp",
        "lxml",
        "HTMLParser",
        "web3",
    ],
    entry_points={},
    extras_require={},
)
