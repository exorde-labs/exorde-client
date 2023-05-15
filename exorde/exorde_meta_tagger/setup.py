from setuptools import setup, find_packages

setup(
    name="exorde_meta_tagger",
    version="0.1.1",
    description="Exorde meta tagger",
    license="MIT",
    packages=find_packages(include=["exorde_meta_tagger"]),
    install_requires=[
        "huggingface_hub==0.13.3",
        "pandas==1.5.3",
        "sentence-transformers==2.2.2",
        "spacy==3.5.1",
        "swifter==1.3.4",
        "tensorflow==2.11.0",
        "torch==1.13.0",
        "vaderSentiment==3.3.2",
    ],
)
