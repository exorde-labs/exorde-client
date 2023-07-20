FROM python:3.10.11

# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y chromium chromium-driver xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromedriver  /usr/local/bin/chromedriver

RUN pip.10 install --no-cache-dir setuptools
RUN pip.10 install --no-cache-dir cyac
RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git' \
        'git+https://github.com/exorde-labs/exorde-client.git'\
        selenium==4.2.0 \
    && pip3.10 install --no-cache-dir --upgrade 'git+https://github.com/JustAnotherArchivist/snscrape.git'

# set display port to avoid crash
ENV DISPLAY=:99

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

## ENTRY POINT IS MAIN.PY
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
COPY keep_alive.sh /exorde/keep_alive.sh
RUN chmod +x /exorde/keep_alive.sh
RUN sed -i 's/\r$//' keep_alive.sh
ENTRYPOINT ["/bin/bash","/exorde/keep_alive.sh"]
