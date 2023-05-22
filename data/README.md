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

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://github.com/exorde-labs/exorde/repo/tree/v0.0.1/exorde/schema/schema.json",
    "type": "object",
    "properties": {
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
            "type": "string",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}"
        },
        "author": {
            "description": "SHA1 encoding of the username assigned as creator of the item on it source plateform",
            "type": "string"
        },
        "created_at": {
            "description": "ISO8601/RFC3339 Date of creation of the item",
            "type": "string",
            "pattern": "^([\\+-]?\\d{4}(?!\\d{2}\\b))((-?)((0[1-9]|1[0-2])(\\3([12]\\d|0[1-9]|3[01]))?|W([0-4]\\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\\d|[12]\\d{2}|3([0-5]\\d|6[1-6])))([T\\s]((([01]\\d|2[0-3])((:?)[0-5]\\d)?|24\\:?00)([\\.,]\\d+(?!:))?)?(\\17[0-5]\\d([\\.,]\\d+)?)?([zZ]|([\\+-])([01]\\d|2[0-3]):?([0-5]\\d)?)?)?)?$"
        },
        "language": {
            "description": "ISO639-1 language code that consist of two lowercase letters",
            "type": "string"
        },
        "title": {
            "description": "Headline of the item",
            "type": "string"
        },
        "domain": {
            "description": "Domain name on which the item was retrieved",
            "type": "string",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}"
        },
        "url": {
            "description": "Uniform-Resource-Locator that identifies the location of the item",
            "type": "string",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}"
        },
        "external_id": {
            "description": "Identifier used by source",
            "type": "string"
        },
        "external_parent_id": {
            "description": "Identifier used by source of parent item",
            "type": "string"
        },
        "classification": {
            "description": "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string"
                    },
                    "weight": {
                        "type": "number"
                    }
                }
            }
        },
        "top_keywords": {
            "description": "The main keywords extracted from the content field",
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "translation": {
            "description": "The content translated in English language",
            "type": "string"
        },
        "embedding": {
            "description": "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model",
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "language_score": {
            "type": "array",
            "items": {
                "description": "Readability score of the text",
                "type": "array",
                "items": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "number"
                    }
                ]
            }
        },
        "age": {
            "description": "Probable age range of the author",
            "type": "object",
            "properties": {
                "below_twenty": {
                    "type": "number"
                },
                "twenty_thirty": {
                    "type": "number"
                },
                "thirty_forty": {
                    "type": "number"
                },
                "forty_more": {
                    "type": "number"
                }
            }
        },
        "irony": {
            "description": "Measure of how much a post is ironic (in %)",
            "type": "object",
            "properties": {
                "non_irony": {
                    "type": "number"
                },
                "irony": {
                    "type": "number"
                }
            }
        },
        "emotion": {
            "description": "Emotion classification of the post, using the go-emotion standard of 28 precise emotions",
            "type": "object",
            "properties": {
                "love": {
                    "type": "number"
                },
                "admiration": {
                    "type": "number"
                },
                "joy": {
                    "type": "number"
                },
                "approval": {
                    "type": "number"
                },
                "caring": {
                    "type": "number"
                },
                "excitement": {
                    "type": "number"
                },
                "gratitude": {
                    "type": "number"
                },
                "desire": {
                    "type": "number"
                },
                "anger": {
                    "type": "number"
                },
                "optimism": {
                    "type": "number"
                },
                "disapproval": {
                    "type": "number"
                },
                "grief": {
                    "type": "number"
                },
                "annoyance": {
                    "type": "number"
                },
                "pride": {
                    "type": "number"
                },
                "curiosity": {
                    "type": "number"
                },
                "neutral": {
                    "type": "number"
                },
                "disgust": {
                    "type": "number"
                },
                "disappointment": {
                    "type": "number"
                },
                "realization": {
                    "type": "number"
                },
                "fear": {
                    "type": "number"
                },
                "relief": {
                    "type": "number"
                },
                "confusion": {
                    "type": "number"
                },
                "remorse": {
                    "type": "number"
                },
                "embarrassement": {
                    "type": "number"
                },
                "suprise": {
                    "type": "number"
                },
                "sadness": {
                    "type": "number"
                },
                "nervousness": {
                    "type": "number"
                }
            }
        },
        "text_type": {
            "description": "Type (category) of the post (article, etc)",
            "type": "object",
            "properties": {
                "assumption": {
                    "type": "number"
                },
                "anecdote": {
                    "type": "number"
                },
                "none": {
                    "type": "number"
                },
                "definition": {
                    "type": "number"
                },
                "testimony": {
                    "type": "number"
                },
                "other": {
                    "type": "number"
                },
                "study": {
                    "type": "number"
                }
            }
        },
        "source_type": {
            "description": "Type (category) of the source that has produced the post",
            "type": "object",
            "properties": {
                "social": {
                    "type": "number"
                },
                "computers": {
                    "type": "number"
                },
                "games": {
                    "type": "number"
                },
                "business": {
                    "type": "number"
                },
                "streaming": {
                    "type": "number"
                },
                "ecommerce": {
                    "type": "number"
                },
                "forums": {
                    "type": "number"
                },
                "photography": {
                    "type": "number"
                },
                "travel": {
                    "type": "number"
                },
                "adult": {
                    "type": "number"
                },
                "law": {
                    "type": "number"
                },
                "sports": {
                    "type": "number"
                },
                "education": {
                    "type": "number"
                },
                "food": {
                    "type": "number"
                },
                "health": {
                    "type": "number"
                }
            }
        },
        "gender": {
            "description": "Probable gender (female or male) of the author",
            "type": "object",
            "properties": {
                "female": {
                    "type": "number"
                },
                "male": {
                    "type": "number"
                }
            }
        },
        "sentiment": {
            "description": "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)",
            "type": "number"
        },
        "collected_at": {
            "description": "ISO8601/RFC3339 Date of collection of the item",
            "type": "string",
            "pattern": "^([\\+-]?\\d{4}(?!\\d{2}\\b))((-?)((0[1-9]|1[0-2])(\\3([12]\\d|0[1-9]|3[01]))?|W([0-4]\\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\\d|[12]\\d{2}|3([0-5]\\d|6[1-6])))([T\\s]((([01]\\d|2[0-3])((:?)[0-5]\\d)?|24\\:?00)([\\.,]\\d+(?!:))?)?(\\17[0-5]\\d([\\.,]\\d+)?)?([zZ]|([\\+-])([01]\\d|2[0-3]):?([0-5]\\d)?)?)?)?$"
        },
        "collection_client_version": {
            "description": "Client identifier with version of client that collected the item.",
            "type": "string"
        },
        "collection_module": {
            "description": "The module that scraped the item.",
            "type": "string"
        }
    }
}
```
