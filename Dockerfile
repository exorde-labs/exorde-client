FROM python:3.10.11

## INSTALL DEPENDENCIES
RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git#subdirectory=data&egg=exorde-data'
RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git'
RUN pip3.10 install --no-cache-dir --upgrade 'git+https://github.com/JustAnotherArchivist/snscrape.git'

## INSTALL ALL MODELS
COPY exorde/pre_install.py /exorde/exorde_install_models.py
WORKDIR /exorde
RUN python3.10 exorde_install_models.py \
    && rm -rf /root/.cache/* \
    && rm -rf /root/.local/cache/*
RUN python3.10 -m spacy download en_core_web_trf \
    && rm -rf /root/.cache/*

## INSTALL THE APP
COPY data /exorde
RUN apt-get update \
    && apt-get upgrade --yes \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

## ENTRY POINT IS MAIN.PY
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
COPY keep_alive.sh /exorde/keep_alive.sh
RUN chmod +x /exorde/keep_alive.sh
ENTRYPOINT ["/bin/bash","/exorde/keep_alive.sh"]
