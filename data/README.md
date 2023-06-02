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

## Item schema
- Items describe entities such as links, videos, posts, comments.
- The item description is valid both for scraping & analysis, therefor the schema also contains the attributes that would be retrieved trough [lab](../lab) processing.
- The [json-schema](https://github.com/exorde-labs/exorde/schema/schema.json) is generated from this [expression](./exorde_data/__init__.py)
- Both `Content` and `Title` are Optional, HOWEVER, one of them has to be existent for an Item to be valid.
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://github.com/exorde-labs/exorde/repo/tree/v0.0.1/exorde/schema/schema.json",
    "type": "object",
    "properties": {
        "created_at": {
            "description": "ISO8601/RFC3339 Date of creation of the item",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,6})?Z$",
            "type": "string"
        },
        "title": {
            "description": "Headline of the item",
            "type": "string"
        },
        "content": {
            "description": "Text body of the item",
            "type": "string"
        },
        "summary": {
            "description": "Short version of the content",
            "type": "string"
        },
        "picture": {
            "description": "Image linked to the item",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}",
            "type": "string"
        },
        "author": {
            "description": "SHA1 encoding of the username assigned as creator of the item on its source platform",
            "type": "string"
        },
        "external_id": {
            "description": "Identifier used by source",
            "type": "string"
        },
        "external_parent_id": {
            "description": "Identifier of parent item, as used by source",
            "type": "string"
        },
        "domain": {
            "description": "Domain name on which the item was retrieved",
            "type": "string"
        },
        "url": {
            "description": "Uniform-Resource-Locator that identifies the location of the item",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}",
            "type": "string"
        }
    },
    "required": [
        "created_at",
        "domain",
        "url"
    ]
}
```
