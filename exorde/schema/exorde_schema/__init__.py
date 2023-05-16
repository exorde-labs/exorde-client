import json
from importlib import metadata

from jschemator import Schema
from jschemator.fields import (
    ArrayField,
    DateTimeField,
    NumberField,
    StringField,
    UrlField,
    Compose,
    ObjectField,
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


class Hate(Schema):
    offensive = NumberField()
    none = NumberField()


class Item(Schema):
    """Posts & Comments both are independants Items"""

    content = StringField(description="Text body of the item")
    author = StringField(
        description="SHA1 of username assigned as creator of the item on the plateform"
    )  # sha1 du username
    created_at = DateTimeField(
        description="ISO8601/RFC3339 Date of creation of the item"
    )
    description = StringField(description="")  # Kecekececa ?
    language = StringField(
        description="ISO639-1 language code that consist of two lowercase letters"
    )  # weak, maybe enum ?
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
        ArrayField(Compose(StringField(), NumberField()))
    )
    top_keywords = ArrayField(StringField())  # yake
    # meta-data (tag)
    translation = StringField()
    embedding = ArrayField(NumberField())

    language_score = ArrayField(
        ArrayField(Compose(StringField(), NumberField()))
    )

    # known size_list
    advertising = ObjectField(Advertising)
    age = ObjectField(Age)
    hate = ObjectField(Hate)
    irony = ObjectField(Irony)
    emotion = ObjectField(Emotion)
    text_type = ObjectField(TextType)
    source_type = ObjectField(SourceType)
    gender = ObjectField(Gender)
    # known size_list

    # unknown size list
    sentiment = NumberField()
    # meta-data (tag) end

    collected_at = DateTimeField(
        description="ISO8601/RFC3339 Date of collection of the item"
    )
    collection_client_version = StringField()


def print_schema():
    print(
        json.dumps(
            Item().json_schema(
                **{
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "$id": f'https://github.com/exorde-labs/exorde/repo/tree/v{metadata.version("exorde_schema")}/exorde/schema/schema.json',
                }
            ),
            indent=4,
        )
    )
