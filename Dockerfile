FROM python:3.10.11

# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y chromium chromium-driver xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromedriver  /usr/local/bin/chromedriver
    
RUN apt-get update && apt-get install -y libhdf5-dev

RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git' \
        'git+https://github.com/exorde-labs/exorde-client.git'\
        selenium==4.2.0 \
        wtpsplit==1.3.0

# Clean cache now that we have installed everything
RUN rm -rf /root/.cache/* \
    && rm -rf /root/.local/cache/*

# set display port to avoid crash
ENV DISPLAY=:99

COPY exorde/pre_install.py /exorde/exorde_install_models.py
WORKDIR /exorde

## INSTALL ALL MODELS: hugginface, langdetect, spacy
RUN mkdir -p /tmp/fasttext-langdetect
RUN wget -O /tmp/fasttext-langdetect/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
RUN python3.10 -m spacy download en_core_web_trf
RUN python3.10 exorde_install_models.py

## INSTALL THE APP
COPY data /exorde

## Set the release version
ARG RELEASE_VERSION
RUN echo ${RELEASE_VERSION} > .release

## SET huggingface transformers cache
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

## ENTRY POINT IS MAIN.PY
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
COPY keep_alive.sh /exorde/keep_alive.sh
RUN chmod +x /exorde/keep_alive.sh
RUN sed -i 's/\r$//' keep_alive.sh
ENTRYPOINT ["/bin/bash","/exorde/keep_alive.sh"]
