FROM python:3.10-slim

#RUN adduser --uid 2000 --gecos "" --disabled-password --quiet exorde_user
#COPY --chown=exorde_user:exorde_user Launcher.py requirements.txt localConfig.json bob.txt /
COPY Launcher.py requirements.txt localConfig.json bob.txt /
RUN apt-get update \
    && apt-get install --no-install-recommends --yes build-essential procps\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
#USER exorde_user

ENTRYPOINT [ "python", "-u", "./Launcher.py"]
