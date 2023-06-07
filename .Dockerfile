FROM python:3.10.11

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
  libnss3 \
  libglib2.0-0 \
  libfontconfig1 \
  libfreetype6 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  xdg-utils \
  gconf-service \
  libasound2 \
  libatk1.0-0 \
  libc6 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libgcc1 \
  libgconf-2-4 \
  libgdk-pixbuf2.0-0 \
  libgl1-mesa-glx \
  libgl1 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-xcb-dev \
  libxcb-dri3-0 \
  libxcomposite-dev \
  libxdamage-dev \
  libxfixes-dev \
  libxrandr-dev \
  libxrender-dev \
  libxslt1.1 \
  libxtst-dev \
  zlib1g-dev \
  xvfb \
  libgbm1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


COPY . /exorde
RUN pip3.10 install --no-cache /exorde/data
RUN pip3.10 install /exorde/data/scraping/reddit
RUN pip3.10 install /exorde/data/scraping/twitter
RUN pip3.10 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git 
RUN pip3.10 install --no-cache /exorde/lab
RUN pip3.10 install --no-cache /exorde/exorde



ENTRYPOINT ["/bin/bash", "-c"] 
# ["exorde"]
# CMD ["-h"]
