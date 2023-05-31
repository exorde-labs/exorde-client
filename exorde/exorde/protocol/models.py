from madtypes import Schema, Annotation

from exorde_data.models import Item as CollectedItem
from exorde_lab.models import TopKeywords, Translation, Analysis


class CollectedAt(str, metaclass=Annotation):
    description = "ISO8601/RFC3339 Date of collection of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}\.[0-9]{1,6}?Z$"


class CollectionClientVersion(str, metaclass=Annotation):
    description = (
        "Client identifier with version of the client that collected the item."
    )
    annotation = str


class CollectionModule(str, metaclass=Annotation):
    description = "Module that scraped the item."
    annotation = str


class Item(Schema):
    item: CollectedItem

    top_keywords: TopKeywords  # yake result
    translation: Translation  # argos_translate
    analysis: Analysis

    collection_client_version: CollectionClientVersion
    collection_module: CollectionModule
    collected_at: CollectedAt
