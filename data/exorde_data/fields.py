from madtypes import AnnotatedAnnotation, Schema


class Content(AnnotatedAnnotation):
    description = "Text body of the item"
    annotation = str


class Summary(AnnotatedAnnotation):
    description = "Short version of the content"
    annotation = str


class Picture(AnnotatedAnnotation):
    description = "Image linked to the item"
    annotation = str


class Author(AnnotatedAnnotation):
    description = "SHA1 encoding of the username assigned as creator of the item on its source platform"
    annotation = str


class CreatedAt(AnnotatedAnnotation):
    description = "ISO8601/RFC3339 Date of creation of the item"
    annotation = str


class Language(AnnotatedAnnotation):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Title(AnnotatedAnnotation):
    description = "Headline of the item"
    annotation = str


class Domain(AnnotatedAnnotation):
    description = "Domain name on which the item was retrieved"
    annotation = str


class Url(AnnotatedAnnotation):
    description = (
        "Uniform-Resource-Locator that identifies the location of the item"
    )
    annotation = str


class Translation(AnnotatedAnnotation):
    description = "The content translated in English language"
    annotation = str


class Sentiment(AnnotatedAnnotation):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class CollectedAt(AnnotatedAnnotation):
    description = "ISO8601/RFC3339 Date of collection of the item"
    annotation = str


class CollectionClientVersion(AnnotatedAnnotation):
    description = (
        "Client identifier with version of the client that collected the item."
    )
    annotation = str


class CollectionModule(AnnotatedAnnotation):
    description = "The module that scraped the item."
    annotation = str


class Topic(AnnotatedAnnotation):
    description = ""
    annotation = str


class Weight(AnnotatedAnnotation):
    description = ""
    annotation = float


class Classification(Schema):
    topic: Topic
    weight: Weight


class ClassificationField(AnnotatedAnnotation):
    description = "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)"
    annotation = list[Classification]


class Embedding(AnnotatedAnnotation):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class TopKeywords(AnnotatedAnnotation):
    description = "The main keywords extracted from the content field"
    annotation = str
