FROM python:3.10.11
COPY . /exorde
WORKDIR /exorde
RUN pip install --upgrade pip
RUN apt-get update

# INSTALL CLIENT CORE
RUN pip3.10 install madtypes
RUN pip3.10 install eth-account
RUN pip3.10 install asyncio
RUN pip3.10 install aiohttp
RUN pip3.10 install lxml
RUN pip3.10 install HTMLParser
RUN pip3.10 install pyyaml
RUN pip3.10 install web3
RUN pip3.10 install fasttext==0.9.2
RUN pip3.10 install fasttext-langdetect==1.0.5
RUN pip3.10 install huggingface_hub==0.14.1
RUN pip3.10 install pandas==1.5.3
RUN pip3.10 install sentence-transformers==2.2.2
RUN pip3.10 install spacy==3.5.1
RUN pip3.10 install swifter==1.3.4
RUN pip3.10 install tensorflow==2.12.0
RUN pip3.10 install torch==1.13.0
RUN pip3.10 install vaderSentiment==3.3.2
RUN pip3.10 install yake==0.4.8
RUN pip3.10 install argostranslate==1.8.0

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



## INSTALL ALL MODELS
RUN python3.10 /exorde/exorde/pre_install.py
RUN python3 -m spacy download en_core_web_trf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

## ENTRY POINT IS MAIN.PY
ENTRYPOINT ["./exorde/exorde/keep_alive.sh"]
