from enum import Enum
from madtypes import MadType

from eth_account.signers.local import LocalAccount
from exorde_data import Item
from web3 import AsyncWeb3
from typing import Optional

from exorde_data import (
    CreatedAt,
    Title,
    Summary,
    Url,
    Author,
    ExternalId,
    ExternalParentId,
    Domain,
    Content,
    Item
)
from dataclasses import dataclass

from typing import Dict, List, Union


@dataclass
class Ponderation:
    enabled_modules: Dict[str, List[str]]
    generic_modules_parameters: Dict[str, Union[int, str, bool]]
    specific_modules_parameters: Dict[str, Dict[str, Union[int, str, bool]]]
    weights: Dict[str, float]
    lang_map: Dict[str, list]  # module_name as key
    new_keyword_alg: int  # weight for #986


class Translated(str, metaclass=MadType):
    description = "The content translated in English language"
    annotation = str


class Language(str, metaclass=MadType):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class CalmTranslation(dict):
    """Result of argos translate"""

    language: Optional[Language]  # uses content or title
    translation: Translated


class Translation(CalmTranslation, metaclass=MadType):
    pass


class Keywords(list, metaclass=MadType):
    description = "The main keywords extracted from the content field"
    annotation = list[str]


class TopKeywords(dict, metaclass=MadType):
    top_keywords: Keywords

class KeywordsWeights(list, metaclass=MadType):
    description = "The main keywords weights extracted from the content field"
    annotation = list[float]

class TopKeywordsWeights(dict, metaclass=MadType):
    top_keywords_weights: KeywordsWeights


class Classification(dict, metaclass=MadType):
    description = "label and score of zero_shot"
    score: float
    label: str


class Sentiment(float, metaclass=MadType):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class Embedding(list, metaclass=MadType):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class LanguageScore(float, metaclass=MadType):
    description = "Readability score of the text"
    annotation = float


class Gender(dict, metaclass=MadType):
    male: float
    female: float
    description = "Probable gender (female or male) of the author"


class SourceType(str, metaclass=MadType):
    description = "Category of the source that has produced the post"
    annotation = str


class TextType(dict, metaclass=MadType):
    assumption: float
    anecdote: float
    none: float
    definition: float
    testimony: float
    other: float
    study: float
    description = "Type (category) of the post (article, etc)"


class Emotion(dict, metaclass=MadType):
    love: float
    admiration: float
    joy: float
    approval: float
    caring: float
    excitement: float
    gratitude: float
    desire: float
    anger: float
    optimism: float
    disapproval: float
    grief: float
    annoyance: float
    pride: float
    curiosity: float
    neutral: float
    disgust: float
    disappointment: float
    realization: float
    fear: float
    relief: float
    confusion: float
    remorse: float
    embarrassment: float
    surprise: float
    sadness: float
    nervousness: float


class Irony(dict, metaclass=MadType):
    irony: float
    non_irony: float
    description = "Measure of how much a post is ironic (in %)"


class Age(dict, metaclass=MadType):
    below_twenty: float
    twenty_thirty: float
    thirty_forty: float
    forty_more: float
    description = "Measure author's age"


class Analysis(dict, metaclass=MadType):
    language_score: LanguageScore
    sentiment: Sentiment
    embedding: Embedding
    gender: Gender
    text_type: TextType
    emotion: Emotion
    irony: Irony
    age: Age


class StaticConfiguration(dict):
    main_address: str
    worker_account: LocalAccount
    protocol_configuration: dict
    network_configuration: dict
    contracts_and_abi: dict
    contracts: dict
    read_web3: AsyncWeb3
    write_web3: AsyncWeb3
    lab_configuration: dict
    gas_cache: dict


class LiveConfiguration(dict):
    """
    Configuration is not a MadType because we do not want to break the
    configuration instantiation if a key is not defined in the python
    code.
    ! it therfor requires a manual checking ; what happens when the user
    is unable to reach the configuration but the protocol is still online ?
    """

    remote_kill: bool
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
    last_notification: str


class Processed(dict, metaclass=MadType):
    translation: Translation
    raw_content: Content
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


class ProtocolItem(dict, metaclass=MadType):
    """Created by a scraping module, it represent a post, article, comment..."""

    created_at: CreatedAt
    title: Optional[Title]  # titre obligatoire si pas de contenu
    raw_content: Optional[Content]
    translated_content: Optional[Content]
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
