from madtypes import MadType
from typing import Optional


class Content(str, metaclass=MadType):
    description = "Text body of the item"
    annotation = str


class Summary(str, metaclass=MadType):
    description = "Short version of the content"
    annotation = str


class Picture(str, metaclass=MadType):
    description = "Image linked to the item"
    annotation = str
    pattern = r"^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}"


class Author(str, metaclass=MadType):
    """todo : SHA1 format check ?"""

    description = "SHA1 encoding of the username assigned as creator of the item on its source platform"
    annotation = str


class CreatedAt(str, metaclass=MadType):
    description = "ISO8601/RFC3339 Date of creation of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,6})?Z$"


class Title(str, metaclass=MadType):
    description = "Headline of the item"
    annotation = str


class Domain(str, metaclass=MadType):
    description = "Domain name on which the item was retrieved"
    annotation = str


class Url(str, metaclass=MadType):
    description = "Uniform-Resource-Locator"
    annotation = str
    pattern = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,32}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"


class Sentiment(str, metaclass=MadType):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class Topic(str, metaclass=MadType):
    description = ""
    annotation = str


class Weight(str, metaclass=MadType):
    description = ""
    annotation = float


class Classification(dict, metaclass=MadType):
    topic: Topic
    weight: Weight


class DescriptedClassification(list, metaclass=MadType):
    description = "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)"
    annotation = list[Classification]


class Embedding(list, metaclass=MadType):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class TopKeywords(list, metaclass=MadType):
    description = "The main keywords extracted from the content field"
    annotation = list[str]


class LanguageScore(float, metaclass=MadType):
    description = "Readability score of the text"
    annotation = float


class Gender(dict, metaclass=MadType):
    male: float
    female: float


class DescriptedGender(Gender, metaclass=MadType):
    description = "Probable gender (female or male) of the author"
    annotation = Gender


class SourceType(dict, metaclass=MadType):
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


class TextType(dict, metaclass=MadType):
    assumption: float
    anecdote: float
    none: float
    definition: float
    testimony: float
    other: float
    study: float


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
    embarrassement: float
    surprise: float
    sadness: float
    nervousness: float


class Irony(dict, metaclass=MadType):
    irony: float
    non_irony: float


class ExternalId(str, metaclass=MadType):
    description = "Identifier used by source"
    annotation = str


class ExternalParentId(str, metaclass=MadType):
    description = "Identifier of parent item, as used by source"
    annotation = str


class Item(dict, metaclass=MadType):
    """Created by a scraping module, it represent a post, article, comment..."""

    created_at: CreatedAt
    title: Optional[Title]  # titre obligatoire si pas de contenu
    content: Optional[Content]
    summary: Optional[Summary]  # <- description or summary available
    picture: Optional[Url]
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


class Analysis(dict, metaclass=MadType):
    langage_score: LanguageScore
    sentiment: Sentiment
    classification: DescriptedClassification
    embedding: Embedding
    gender: DescriptedGender
    source_type: SourceType
    text_type: TextType
    emotion: Emotion
    irony: Irony
    # age
