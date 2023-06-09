FROM python:3.10.11
COPY . /exorde
WORKDIR /exorde
RUN pip install --upgrade pip
RUN apt-get update

# INSTALL CLIENT CORE
RUN pip3.10 install madtypes==0.0.9
RUN pip3.10 install eth-account
RUN pip3.10 install asyncio
RUN pip3.10 install aiohttp
RUN pip3.10 install pyyaml
RUN pip3.10 install web3

RUN pip3.10 install /exorde/data
## INSTALL SCRAPING MODULES
RUN pip3.10 install /exorde/data/scraping/reddit
RUN pip3.10 install /exorde/data/scraping/twitter
RUN pip3.10 install /exorde/data/scraping/4chan
## snscrape temporary trick
RUN pip3.10 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git

# INSTALL DATA SYSTEMS
RUN pip3.10 install transformers
RUN pip3.10 install huggingface_hub
RUN pip3.10 install torch

RUN pip3.10 install /exorde/lab

## INSTALL ALL MODELS
RUN python3.10 /exorde/lab/exorde_lab/analysis/install.py
RUN python3.10 /exorde/lab/exorde_lab/translation/install.py
RUN python3 -m spacy download en_core_web_trf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

## ENTRY POINT IS MAINT.PY
ENTRYPOINT ["python3", "/exorde/exorde/main.py"]
