FROM python:3.10.11
COPY data /exorde
WORKDIR /exorde
RUN pip install --upgrade pip
RUN apt-get update

RUN pip3.10 install git+https://github.com/exorde-labs/exorde-client.git#subdirectory=data&egg=exorde-data
RUN pip3.10 install git+https://github.com/exorde-labs/exorde-client.git#subdirectory=exorde&egg=exorde
RUN pip3.10 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git

## INSTALL ALL MODELS
RUN exorde_install_models
RUN python3 -m spacy download en_core_web_trf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

## ENTRY POINT IS MAIN.PY
ENTRYPOINT ["/exorde/keep_alive.sh"]
