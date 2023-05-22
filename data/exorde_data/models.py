from jschemator import Schema
from enum import Enum
from jschemator.fields import (
    ArrayField,
    DateTimeField,
    NumberField,
    StringField,
    UrlField,
    Compose,
    ObjectField,
    EnumField,
)


# TODO: ChildField
# TODO: Description pour chaque champs
# TODO: $id


class Emotion(Schema):
    love = NumberField()
    admiration = NumberField()
    joy = NumberField()
    approval = NumberField()
    caring = NumberField()
    excitement = NumberField()
    gratitude = NumberField()
    desire = NumberField()
    anger = NumberField()
    optimism = NumberField()
    disapproval = NumberField()
    grief = NumberField()
    annoyance = NumberField()
    pride = NumberField()
    curiosity = NumberField()
    neutral = NumberField()
    disgust = NumberField()
    disappointment = NumberField()
    realization = NumberField()
    fear = NumberField()
    relief = NumberField()
    confusion = NumberField()
    remorse = NumberField()
    embarrassement = NumberField()
    suprise = NumberField()
    sadness = NumberField()
    nervousness = NumberField()


class Advertising(Schema):
    advertise = NumberField()
    recommend = NumberField()


class Irony(Schema):
    non_irony = NumberField()
    irony = NumberField()


class TextType(Schema):
    assumption = NumberField()
    anecdote = NumberField()
    none = NumberField()
    definition = NumberField()
    testimony = NumberField()
    other = NumberField()
    study = NumberField()


class SourceType(Schema):
    social = NumberField()
    computers = NumberField()
    games = NumberField()
    business = NumberField()
    streaming = NumberField()
    ecommerce = NumberField()
    forums = NumberField()
    photography = NumberField()
    travel = NumberField()
    adult = NumberField()
    law = NumberField()
    sports = NumberField()
    education = NumberField()
    food = NumberField()
    health = NumberField()


class Age(Schema):
    below_twenty = NumberField()
    twenty_thirty = NumberField()
    thirty_forty = NumberField()
    forty_more = NumberField()


class Gender(Schema):
    female = NumberField()
    male = NumberField()


class Classification(Schema):
    topic = StringField()
    weight = NumberField()


class Item(Schema):
    """Posts & Comments both are independants Items"""

    content = StringField(description="Text body of the item")
    summary = StringField(description="Short version of the content")
    picture = UrlField(description="Image linked to the item")
    author = StringField(
        description="SHA1 encoding of the username assigned as creator of the item on it source plateform"
    )
    created_at = DateTimeField(
        description="ISO8601/RFC3339 Date of creation of the item"
    )
    language = StringField(
        description="ISO639-1 language code that consist of two lowercase letters"
    )
    title = StringField(description="Headline of the item")
    domain = UrlField(
        description="Domain name on which the item was retrieved"
    )
    url = UrlField(
        description="Uniform-Resource-Locator that identifies the location of the item"
    )
    external_id = StringField(description="Identifier used by source")
    external_parent_id = StringField(
        description="Identifier used by source of parent item"
    )
    # classification = zero_shot
    classification = ArrayField(
        ObjectField(Classification),
        description="Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)",
    )
    top_keywords = ArrayField(
        StringField(),
        description="The main keywords extracted from the content field",
    )  # yake-generated

    # meta-data (tagger)
    translation = StringField(
        description="The content translated in English language"
    )

    embedding = ArrayField(
        NumberField(),
        description="Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model",
    )

    language_score = ArrayField(
        ArrayField(
            Compose(StringField(), NumberField()),
            description="Readability score of the text",
        )
    )

    # known size_list
    age = ObjectField(Age, description="Probable age range of the author")
    irony = ObjectField(
        Irony, description="Measure of how much a post is ironic (in %)"
    )
    emotion = ObjectField(
        Emotion,
        description="Emotion classification of the post, using the go-emotion standard of 28 precise emotions",
    )
    text_type = ObjectField(
        TextType, description="Type (category) of the post (article, etc)"
    )
    source_type = ObjectField(
        SourceType,
        description="Type (category) of the source that has produced the post",
    )
    gender = ObjectField(
        Gender, description="Probable gender (female or male) of the author"
    )

    # unknown size list
    sentiment = NumberField(
        description="Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    )
    # meta-data (tag) end

    collected_at = DateTimeField(
        description="ISO8601/RFC3339 Date of collection of the item"
    )
    collection_client_version = StringField(
        description="Client identifier with version of client that collected the item."
    )
    collection_module = StringField(
        description="The module that scraped the item."
    )
