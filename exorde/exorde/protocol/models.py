from enum import Enum
from madtypes import MadType

from exorde_data.models import Item as CollectedItem
from exorde_lab.models import (
    TopKeywords,
    Translation,
    Analysis,
    Classification,
)


class CollectedAt(str, metaclass=MadType):
    description = "ISO8601/RFC3339 Date of collection of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}\.[0-9]{1,6}?Z$"


class CollectionClientVersion(str, metaclass=MadType):
    description = (
        "Client identifier with version of the client that collected the item."
    )
    annotation = str


class CollectionModule(str, metaclass=MadType):
    description = "Module that scraped the item."
    annotation = str


class BatchKindEnum(Enum):
    SPOTTING = "SPOTTING"
    VALIDATION = "VALIDATION"


from madtypes import subtract_fields

ProtocolTranslation = subtract_fields("translation")(Translation)
ContentLessItem = subtract_fields("content")(CollectedItem)


class ProtocolItem(ContentLessItem, ProtocolTranslation):
    pass


class ProtocolAnalysis(Classification, Analysis, TopKeywords):
    pass


class ProcessedItem(dict, metaclass=MadType):
    item: ProtocolItem
    analysis: ProtocolAnalysis
    collection_client_version: CollectionClientVersion
    collection_module: CollectionModule
    collected_at: CollectedAt


class Batch(dict, metaclass=MadType):
    items: list[ProcessedItem]
    kind: BatchKindEnum
