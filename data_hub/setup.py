from setuptools import setup, find_packages

setup(
    name="exorde_data_hub",
    version="0.1.1",
    description="Exorde data hub tools",
    license="MIT",
    packages=find_packages(include=["meta_tagger", "translation", "xyake"]),
    install_requires=[
        "pybind11>=2.2",
        "huggingface_hub==0.13.3",
        "pandas==1.5.3",
        "sentence-transformers==2.2.2",
        "spacy==3.5.1",
        "swifter==1.3.4",
        "tensorflow",
        "torch==1.13.0",
        "vaderSentiment==3.3.2",
        "yake",
        "fasttext-langdetect",
        "argostranslate",
    ],
)
