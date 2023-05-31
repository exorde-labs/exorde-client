<img src="https://img.shields.io/badge/how%20to-customize%20the%20client%20behavior-yellowgreen?style=for-the-badge" />

Coming up soon !

## Schema used by the protocol
```json
{
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "object",
                        "properties": {
                            "created_at": {
                                "description": "ISO8601/RFC3339 Date of creation of the item",
                                "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}\\.[0-9]{1,6}?Z$",
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
                    },
                    "top_keywords": {
                        "description": "The main keywords extracted from the content field",
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "uniqueItems": true
                    },
                    "translation": {
                        "type": "object",
                        "properties": {
                            "language": {
                                "description": "ISO639-1 language code that consists of two lowercase letters",
                                "type": "string"
                            },
                            "translation": {
                                "description": "The content translated in English language",
                                "type": "string"
                            }
                        },
                        "required": [
                            "translation"
                        ]
                    },
                    "analysis": {
                        "type": "object",
                        "properties": {
                            "classification": {
                                "description": "label and score of zero_shot",
                                "type": "array",
                                "items": [
                                    {
                                        "type": "string"
                                    },
                                    {
                                        "type": "number"
                                    }
                                ]
                            },
                            "langage_score": {
                                "description": "Readability score of the text",
                                "type": "number"
                            },
                            "sentiment": {
                                "description": "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)",
                                "type": "number"
                            },
                            "embedding": {
                                "description": "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model",
                                "type": "array",
                                "items": {
                                    "type": "number"
                                }
                            },
                            "gender": {
                                "description": "Probable gender (female or male) of the author",
                                "type": "object",
                                "properties": {
                                    "male": {
                                        "type": "number"
                                    },
                                    "female": {
                                        "type": "number"
                                    }
                                },
                                "required": [
                                    "male",
                                    "female"
                                ]
                            },
                            "source_type": {
                                "description": "Category of the source that has produced the post",
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
                                },
                                "required": [
                                    "social",
                                    "computers",
                                    "games",
                                    "business",
                                    "streaming",
                                    "ecommerce",
                                    "forums",
                                    "photography",
                                    "travel",
                                    "adult",
                                    "law",
                                    "sports",
                                    "education",
                                    "food",
                                    "health"
                                ]
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
                                },
                                "required": [
                                    "assumption",
                                    "anecdote",
                                    "none",
                                    "definition",
                                    "testimony",
                                    "other",
                                    "study"
                                ]
                            },
                            "emotion": {
                                "description": "",
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
                                    "surprise": {
                                        "type": "number"
                                    },
                                    "sadness": {
                                        "type": "number"
                                    },
                                    "nervousness": {
                                        "type": "number"
                                    }
                                },
                                "required": [
                                    "love",
                                    "admiration",
                                    "joy",
                                    "approval",
                                    "caring",
                                    "excitement",
                                    "gratitude",
                                    "desire",
                                    "anger",
                                    "optimism",
                                    "disapproval",
                                    "grief",
                                    "annoyance",
                                    "pride",
                                    "curiosity",
                                    "neutral",
                                    "disgust",
                                    "disappointment",
                                    "realization",
                                    "fear",
                                    "relief",
                                    "confusion",
                                    "remorse",
                                    "embarrassement",
                                    "surprise",
                                    "sadness",
                                    "nervousness"
                                ]
                            },
                            "irony": {
                                "description": "Measure of how much a post is ironic (in %)",
                                "type": "object",
                                "properties": {
                                    "irony": {
                                        "type": "number"
                                    },
                                    "non_irony": {
                                        "type": "number"
                                    }
                                },
                                "required": [
                                    "irony",
                                    "non_irony"
                                ]
                            },
                            "age": {
                                "description": "Measure author's age",
                                "type": "object",
                                "properties": {
                                    "bellow_twenty": {
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
                                },
                                "required": [
                                    "bellow_twenty",
                                    "twenty_thirty",
                                    "thirty_forty",
                                    "forty_more"
                                ]
                            }
                        },
                        "required": [
                            "classification",
                            "langage_score",
                            "sentiment",
                            "embedding",
                            "gender",
                            "source_type",
                            "text_type",
                            "emotion",
                            "irony",
                            "age"
                        ]
                    },
                    "collection_client_version": {
                        "description": "Client identifier with version of the client that collected the item.",
                        "type": "string"
                    },
                    "collection_module": {
                        "description": "Module that scraped the item.",
                        "type": "string"
                    },
                    "collected_at": {
                        "description": "ISO8601/RFC3339 Date of collection of the item",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}\\.[0-9]{1,6}?Z$",
                        "type": "string"
                    }
                },
                "required": [
                    "item",
                    "top_keywords",
                    "translation",
                    "analysis",
                    "collection_client_version",
                    "collection_module",
                    "collected_at"
                ]
            }
        },
        "kind": {
            "type": "string",
            "enum": [
                "SPOTTING",
                "VALIDATION"
            ]
        }
    },
    "required": [
        "items",
        "kind"
    ]
}
```
