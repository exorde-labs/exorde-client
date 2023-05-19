<img src="https://img.shields.io/badge/how%20to-mine%20EXD-yellowgreen?style=for-the-badge" />

Exorde maintains a [web3](https://ethereum.org/en/web3/) protocol which aim is to orchestrate scraping at scale.

- [EXD](https://www.coinbase.com/fr/price/exorde) evaluation
- [White-Paper](https://uploads-ssl.webflow.com/60aec7ee1888490c4031cbcd/63d7dff65fc5c9f3f2633470_Exorde_Whitepaper_2023.pdf)
- [API](https://exorde.io/)

### Requierements
- at least 8 GB of virtual memory
- python 3.10

### Distribution

#### [pip](https://pypi.org/)
- Our [instalation test](https://github.com/exorde-labs/exorde/blob/mangle/.github/workflows/test.yml) is an example of installation using ubuntu. 
- On github workflows, the process of installation took around 5 minutes.

[![Package installation test](https://github.com/exorde-labs/exorde/actions/workflows/installation-test.yml/badge.svg)](https://github.com/exorde-labs/exorde/actions/workflows/installation-test.yml)
```bash
pip3.10 install exorde
```

#### [docker](https://www.docker.com/)
```bash
docker run exorde
```
### Usage
```bash
exorde -h
```
