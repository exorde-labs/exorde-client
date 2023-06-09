from enum import Enum
from madtypes import MadType

from exorde_data.models import Item
from exorde_lab.models import Keywords, Classification, Analysis, Translation

from typing import Optional


class Configuration(dict):
    """
    Configuration is not a MadType because we do not want to break the
    configuration instantiation if a key is not defined in the python
    code.
    ! it therfor requires a manual checking ; what happens when the user
    is unable to reach the configuration but the protocol is still online ?
    """

    online: bool
    batch_size: int
    last_info: Optional[str]
    worker_version: Optional[str]
    protocol_version: Optional[str]
    expiration_delta: Optional[int]  # data freshness
    target: Optional[str]
    default_gas_price: Optional[int]
    default_gas_amount: Optional[int]
    gas_cap_min: Optional[int]
    inter_spot_delay_seconds: int


class Processed(dict, metaclass=MadType):
    translation: Translation
    top_keywords: Keywords
    classification: Classification
    item: Item


class CollectedAt(str, metaclass=MadType):
    description = "ISO8601/RFC3339 Date of collection of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,6})?Z$"


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


from exorde_data.models import (
    CreatedAt,
    Title,
    Summary,
    Url,
    Author,
    ExternalId,
    ExternalParentId,
    Domain,
)
from exorde_lab.translation.models import Language
from typing import Optional


class ProtocolItem(dict, metaclass=MadType):
    """Created by a scraping module, it represent a post, article, comment..."""

    created_at: CreatedAt
    title: Optional[Title]  # titre obligatoire si pas de contenu
    summary: Optional[Summary]  # <- description or summary available
    picture: Optional[Url]
    author: Optional[Author]
    external_id: Optional[ExternalId]
    external_parent_id: Optional[ExternalParentId]
    domain: Domain
    url: Url
    language: Language
    # type: Type # work in progress

    def is_valid(self, **kwargs) -> bool:
        """object is valid if we either have content or title"""
        return (
            False
            if not kwargs.get("content", None)
            and not kwargs.get("title", None)
            else True
        )


from exorde_lab.analysis.models import (
    Sentiment,
    Embedding,
    Gender,
    SourceType,
    TextType,
    Emotion,
    Irony,
    Age,
    LanguageScore,
)


class ProtocolAnalysis(dict, metaclass=MadType):
    classification: Classification
    top_keywords: Keywords
    language_score: LanguageScore
    sentiment: Sentiment
    embedding: Embedding
    gender: Gender
    source_type: SourceType
    text_type: TextType
    emotion: Emotion
    irony: Irony
    age: Age


class ProcessedItem(dict, metaclass=MadType):
    item: ProtocolItem
    analysis: ProtocolAnalysis
    collection_client_version: CollectionClientVersion
    collection_module: CollectionModule
    collected_at: CollectedAt


class Batch(dict, metaclass=MadType):
    items: list[ProcessedItem]
    kind: BatchKindEnum
