FROM python:latest

RUN pip install exorde

ENTRYPOINT ["exorde"]
CMD ["-h"]
