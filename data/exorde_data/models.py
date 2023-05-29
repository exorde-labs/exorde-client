from madtypes import Annotation, Schema


class Content(Annotation):
    description = "Text body of the item"
    annotation = str


class Summary(Annotation):
    description = "Short version of the content"
    annotation = str


class Picture(Annotation):
    description = "Image linked to the item"
    annotation = str


class Author(Annotation):
    description = "SHA1 encoding of the username assigned as creator of the item on its source platform"
    annotation = str


class CreatedAt(Annotation):
    description = "ISO8601/RFC3339 Date of creation of the item"
    annotation = str


class Language(Annotation):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Title(Annotation):
    description = "Headline of the item"
    annotation = str


class Domain(Annotation):
    description = "Domain name on which the item was retrieved"
    annotation = str


class Url(Annotation):
    description = (
        "Uniform-Resource-Locator that identifies the location of the item"
    )
    annotation = str


class Translation(Annotation):
    description = "The content translated in English language"
    annotation = str


class Sentiment(Annotation):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class CollectedAt(Annotation):
    description = "ISO8601/RFC3339 Date of collection of the item"
    annotation = str


class CollectionClientVersion(Annotation):
    description = (
        "Client identifier with version of the client that collected the item."
    )
    annotation = str


class CollectionModule(Annotation):
    description = "The module that scraped the item."
    annotation = str


class Topic(Annotation):
    description = ""
    annotation = str


class Weight(Annotation):
    description = ""
    annotation = float


class Classification(Schema):
    topic: Topic
    weight: Weight


class DescriptedClassification(Annotation):
    description = "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)"
    annotation = list[Classification]


class Embedding(Annotation):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class TopKeywords(Annotation):
    description = "The main keywords extracted from the content field"
    annotation = str


class LanguageScore(Annotation):
    description = "Readability score of the text"
    annotation = float


class Gender(Schema):
    male: float
    female: float


class DescriptedGender(Annotation):
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


class DescriptedSourceType(Annotation):
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


class DescriptedTextType(Annotation):
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
    suprise: float
    sadness: float
    nervousness: float


class DescriptedEmotion(Annotation):
    description = ""
    annotation = Emotion


class Irony(Schema):
    irony: float
    non_irony: float


class DescriptedIrony(Annotation):
    description = "Measure of how much a post is ironic (in %)"
    annotation = Irony


class Item(Schema):
    content: Content
    translation: Translation
    language: Language
    summary: Summary
    picture: Picture
    author: Author
    title: Title
    domain: Domain
    url: Url
    created_at: CreatedAt
    collected_at: CollectedAt
    collection_client_version: CollectionClientVersion
    collection_module: CollectionModule
    sentiment: Sentiment
    classification: DescriptedClassification
    embedding: Embedding
    top_keywords: TopKeywords
    langage_score: LanguageScore
    gender: DescriptedGender
    source_type: DescriptedSourceType
    text_type: DescriptedTextType
    emotion: DescriptedEmotion
    irony: DescriptedIrony
