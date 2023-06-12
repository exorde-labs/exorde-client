from setuptools import find_packages, setup

setup(
    name="exorde_data",
    version="0.0.1",
    packages=find_packages(include=["exorde_data"]),
    install_requires=[
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
    entry_points={
        "console_scripts": ["exorde_data = exorde_data.__init__:print_schema"]
    },
    extras_require={
        "reddit": ["ap98j3envoubi3fco1kc"],
        "twitter": ["a7df32de3a60dfdb7a0b"],
        "4chan": ["ch4875eda56be56000ac"],
        "dev": ["pytest"],
    },
)
