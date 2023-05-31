from madtypes import Annotation, Schema
from typing import Optional


class Content(str, metaclass=Annotation):
    description = "Text body of the item"
    annotation = str


class Summary(str, metaclass=Annotation):
    description = "Short version of the content"
    annotation = str


class Picture(str, metaclass=Annotation):
    description = "Image linked to the item"
    annotation = str
    pattern = r"^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}"


class Author(str, metaclass=Annotation):
    """todo : SHA1 format check ?"""

    description = "SHA1 encoding of the username assigned as creator of the item on its source platform"
    annotation = str


class CreatedAt(str, metaclass=Annotation):
    description = "ISO8601/RFC3339 Date of creation of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}\.[0-9]{1,6}?Z$"


class Title(str, metaclass=Annotation):
    description = "Headline of the item"
    annotation = str


class Domain(str, metaclass=Annotation):
    description = "Domain name on which the item was retrieved"
    annotation = str


class Url(str, metaclass=Annotation):
    description = (
        "Uniform-Resource-Locator that identifies the location of the item"
    )
    annotation = str
    pattern = r"^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}"


class Sentiment(str, metaclass=Annotation):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


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
    description = "The module that scraped the item."
    annotation = str


class Topic(str, metaclass=Annotation):
    description = ""
    annotation = str


class Weight(str, metaclass=Annotation):
    description = ""
    annotation = float


class Classification(Schema):
    topic: Topic
    weight: Weight


class DescriptedClassification(list, metaclass=Annotation):
    description = "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)"
    annotation = list[Classification]


class Embedding(list, metaclass=Annotation):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class TopKeywords(list, metaclass=Annotation):
    description = "The main keywords extracted from the content field"
    annotation = list[str]


class LanguageScore(float, metaclass=Annotation):
    description = "Readability score of the text"
    annotation = float


class Gender(Schema):
    male: float
    female: float


class DescriptedGender(Gender, metaclass=Annotation):
    description = "Probable gender (female or male) of the author"
    annotation = Gender


class SourceType(Schema):
    social: float
    computers: float
    games: float
    business: float
    streaming: float
    ecommerce: float
    forums: float
    photography: float
    travel: float
    adult: float
    law: float
    sports: float
    education: float
    food: float
    health: float


class DescriptedSourceType(SourceType, metaclass=Annotation):
    description = "Category of the source that has produced the post"
    annotation = SourceType


class TextType(Schema):
    assumption: float
    anecdote: float
    none: float
    definition: float
    testimony: float
    other: float
    study: float


class DescriptedTextType(TextType, metaclass=Annotation):
    description = "Type (category) of the post (article, etc)"
    annotation = TextType


class Emotion(Schema):
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
    embarrassement: float
    surprise: float
    sadness: float
    nervousness: float


class DescriptedEmotion(Emotion, metaclass=Annotation):
    description = ""
    annotation = Emotion


class Irony(Schema):
    irony: float
    non_irony: float


class DescriptedIrony(Irony, metaclass=Annotation):
    description = "Measure of how much a post is ironic (in %)"
    annotation = Irony


# todo:
# unique items (pas de doublons dans la liste) -> type set


class ExternalId(str, metaclass=Annotation):
    description = "Identifier used by source"
    annotation = str


class ExternalParentId(str, metaclass=Annotation):
    description = "Identifier of parent item, as used by source"
    annotation = str


class Item(Schema):
    """Created by a scraping module, it represent a post, article, comment..."""

    created_at: CreatedAt
    title: Optional[Title]  # titre obligatoire si pas de contenu
    content: Optional[Content]
    summary: Optional[Summary]  # <- description or summary available
    picture: Optional[Picture]  # illustration picture # URL
    author: Optional[Author]
    external_id: Optional[ExternalId]
    external_parent_id: Optional[ExternalParentId]
    domain: Domain
    url: Url
    # type: Type # work in progress

    def is_valid(self, **kwargs) -> bool:
        """object is valid if we either have content or title"""
        return (
            False
            if not kwargs.get("content", None)
            and not kwargs.get("title", None)
            else True
        )


class Translated(str, metaclass=Annotation):
    description = "The content translated in English language"
    annotation = str


class Language(str, metaclass=Annotation):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Translation(Schema):
    language: Optional[Language]  # content or title
    translation: Translated


class Analysis(Schema):
    langage_score: LanguageScore
    sentiment: Sentiment
    classification: DescriptedClassification
    embedding: Embedding
    gender: DescriptedGender
    source_type: DescriptedSourceType
    text_type: DescriptedTextType
    emotion: DescriptedEmotion
    irony: DescriptedIrony
    # age


class Analyzed(Schema):
    item: Item

    top_keywords: TopKeywords
    translation: Translation
    analysis: Analysis

    collection_client_version: CollectionClientVersion
    collection_module: CollectionModule
    collected_at: CollectedAt
