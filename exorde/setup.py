from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="exorde",
    version="0.0.1",
    author="Exorde Labs",
    author_email="hello@exordelabs.com",
    description="The AI-based client to mine data and power the Exorde Network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/exorde-labs/exorde-client",
    entry_points={
        "console_scripts": [
            "exorde = main:run",
            "exorde_install_models = pre_install:pre_install",
        ]
    },
    packages=find_packages(),
    install_requires=[
        "madtypes",
        "eth-account",
        "asyncio",
        "aiohttp",
        "lxml",
        "HTMLParser",
        "pyyaml",
        "web3",
        "fasttext==0.9.2",
        "fasttext-langdetect==1.0.5",
        "huggingface_hub==0.14.1",
        "pandas==1.5.3",
        "sentence-transformers==2.2.2",
        "spacy==3.5.1",
        "swifter==1.3.4",
        "tensorflow==2.12.0",
        "torch==1.13.0",
        "vaderSentiment==3.3.2",
        "yake==0.4.8",
        "argostranslate==1.8.0",
    ],
    python_requires=">=3.10",
)
