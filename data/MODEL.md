<img src="https://img.shields.io/badge/how%20to-scrap-blue?style=for-the-badge" />

Exorde maintain and publish a modular and unified interface for scraping from different sources.

- each source has it's own package listed in [modules](./modules)
- every package has a unified usage interface
- each return the same [Item](../schema) class

## Distribution

To distribute the modules safely without being exposed to name spamming, all the packages are published on pypi using a random UUID, and then made available trough the exorde_scraping module.

For instance, to install the reddit scraping module, you would do
```bash
pip3 install exorde_scrapping[reddit]
```

The python module would then be availble at

```python
from exorde_scrapping import reddit
```


## ![https://github.com/exorde-labs/exorde/actions/workflows/interface-test.yaml](https://github.com/exorde-labs/exorde/actions/workflows/interface-test.yaml/badge.svg)



We [test](tests/test_unified_interface.py) every module in `data/scraping` with these specifications:

- An exorde_scraping module provide a query function which takes an URL and returns an AsyncGenerator.
- The AsyncGenerator returns Items as defind below.
```python
query(url: str) -> AsyncGenerator[Item, None]
```

## Unified item schema
- Items describe entities such as links, videos, posts, comments.
- The item description is valid both for scraping & analysis, therefor the schema also contains the attributes that would be retrieved trough [lab](../lab) processing.
- The [json-schema](https://github.com/exorde-labs/exorde/schema/schema.json) is generated from this [expression](./exorde_data/__init__.py)

