FROM python:3.10.11

COPY . /exorde

RUN pip3.10 install /exorde

# RUN pip3.10 --no-cache install exorde==0.1.1

RUN apt-get update && apt-get install -y \
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
  libgbm1

ENTRYPOINT ["exorde"]
CMD ["-h"]
