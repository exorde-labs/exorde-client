FROM python:3.9

ADD Launcher.py .
ADD requirements.txt .
ADD localConfig.json .

RUN pip install -r requirements.txt 

ENTRYPOINT [ "python", "./Launcher.py"]
