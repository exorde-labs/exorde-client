FROM python:3.10.11
COPY data /exorde
WORKDIR /exorde
RUN pip install --upgrade pip
RUN apt-get update

RUN pip3.10 install 'git+https://github.com/exorde-labs/exorde-client.git#subdirectory=data&egg=exorde-data'
RUN pip3.10 install 'git+https://github.com/exorde-labs/exorde-client.git'
RUN pip3.10 install --upgrade 'git+https://github.com/JustAnotherArchivist/snscrape.git'
COPY exorde/pre_install.py /exorde/exorde_install_models.py
## INSTALL ALL MODELS
RUN python3.10 exorde_install_models.py
RUN python3 -m spacy download en_core_web_trf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

## ENTRY POINT IS MAIN.PY
COPY keep_alive.sh /exorde/keep_alive.sh
RUN chmod +x /exorde/keep_alive.sh
ENTRYPOINT ["/bin/sh","/exorde/keep_alive.sh"]
