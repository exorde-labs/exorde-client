from setuptools import setup, find_packages

setup(
    name="exorde_lab",
    version="0.1.1",
    description="Exorde data hub tools",
    license="MIT",
    packages=find_packages(
        include=[
            "exorde_lab.meta_tagger",
            "exorde_lab.translation",
            "exorde_lab.xyake",
            "exorde_lab.preprocess",
            "exorde_lab.keywords",
            "exorde_lab.classification",
        ]
    ),
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
        "console_scripts": [
            "install_translation = exorde_lab.translation.install:install_translation_modules"
        ]
    },
    setup_requires=["pybind11"],
)
