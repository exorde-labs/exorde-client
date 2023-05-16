import json

from jschemator import Schema
from jschemator.fields import (
    ArrayField,
    DateTimeField,
    IntegerField,
    NumberField,
    StringField,
    UrlField,
    Compose,
)


class Item(Schema):
    """Posts & Comments both are independants Items"""

    content = StringField()
    author = StringField()  # sha1 du username
    creation_datetime = DateTimeField()
    description = StringField()
    language = StringField()  # weak, maybe enum ?
    title = StringField()
    domain = UrlField()
    url = UrlField()
    internal_id = StringField()
    internal_parent_id = StringField()
    nb_comments = IntegerField()
    nb_likes = IntegerField()
    nb_shared = IntegerField()

    # classification = zero_shot
    classification = ArrayField(
        ArrayField(Compose(StringField(), NumberField()))
    )
    # meta-data (tag)
    translation = StringField()
    embedding = ArrayField(NumberField())
    advertising = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    emotion = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    irony = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    language_score = ArrayField(
        ArrayField(Compose(StringField(), NumberField()))
    )
    text_type = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    source_type = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    sentiment = NumberField()
    age = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    gender = ArrayField(ArrayField(Compose(StringField(), NumberField())))
    hate = ArrayField(ArrayField(Compose(StringField(), NumberField())))

    # meta-data (tag) end

    collection_datetime = DateTimeField()
    collection_client_version = StringField()


def print_schema():
    print(json.dumps(Item(**{"$id": "foo"}).json_schema(), indent=4))
