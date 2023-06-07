FROM python:3.10.11
COPY . /exorde
WORKDIR /exorde
RUN apt-get update
RUN apt-get install zsh -y
RUN pip3.10 install /exorde/data
RUN pip3.10 install /exorde/data/scraping/reddit
RUN pip3.10 install /exorde/data/scraping/twitter
RUN pip3.10 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git 
RUN pip3.10 install /exorde/lab
RUN pip3.10 install /exorde/exorde
ENTRYPOINT ["/bin/zsh"]
