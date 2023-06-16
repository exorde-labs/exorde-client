FROM python:3.10.11

# ## INSTALL DEPENDENCIES
# RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git#subdirectory=data&egg=exorde-data'
# RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git'
RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git@new_sources#subdirectory=data&egg=exorde-data'
RUN pip3.10 install --no-cache-dir 'git+https://github.com/exorde-labs/exorde-client.git@new_sources'

RUN pip3.10 install --no-cache-dir --upgrade 'git+https://github.com/JustAnotherArchivist/snscrape.git'

# install selenium
RUN pip install selenium==4.2.0

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update -y \
    && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver

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
RUN apt-get update \
    && apt-get upgrade --yes \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

## ENTRY POINT IS MAIN.PY
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
COPY keep_alive.sh /exorde/keep_alive.sh
RUN chmod +x /exorde/keep_alive.sh
ENTRYPOINT ["/bin/bash","/exorde/keep_alive.sh"]
