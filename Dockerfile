FROM python:3.10.11 AS exorde_lab
COPY . /exorde
WORKDIR /exorde
RUN pip install --upgrade pip
RUN apt-get update

RUN pip3.10 install transformers
RUN pip3.10 install huggingface_hub
RUN pip3.10 install torch

RUN pip3.10 install /exorde/lab

RUN python3.10 /exorde/lab/exorde_lab/analysis/install.py
RUN python3.10 /exorde/lab/exorde_lab/translation/install.py
RUN python3 -m spacy download en_core_web_trf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

RUN pip3.10 install exorde/data
RUN pip3.10 install /exorde/data/scraping/reddit
RUN pip3.10 install /exorde/data/scraping/twitter
RUN pip3.10 install /exorde/data/scrapping/4chan
RUN pip3.10 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git


ENTRYPOINT ["python3", "/exorde/exorde/main.py"]
