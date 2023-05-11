from enum import Enum
import json

from schemator import (
    ArrayField,
    DateTimeField,
    EnumField,
    IntegerField,
    JsonSchema,
    StringField,
    UrlField,
)


class MediaType(Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    POST = "POST"
    COMMENT = "COMMENT"


class Trivalent(Enum):
    UNKNOWN = "UNKNOWN"
    TRUE = "TRUE"
    FALSE = "FALSE"


class Item(JsonSchema):
    content = StringField()
    author = StringField()  # sha1 du username
    controversial = EnumField(Trivalent)
    creation_date_time = DateTimeField()
    description = StringField()
    language = StringField()  # weak, maybe enum ?
    title = StringField()
    url = UrlField()
    internal_id = StringField()
    internal_parent_id = StringField()
    media_type = EnumField(MediaType)
    nb_comments = IntegerField()
    nb_likes = IntegerField()
    nb_shared = IntegerField()
    # classification = zero_shot
    # metadata = tag
    top_keywords = ArrayField(StringField())
    spotterCountry = StringField()


# comments are different items

if __name__ == "__main__":
    e = Item()
    e.author = "foo"
    print(e.author)
    print(json.dumps(e.schema(), indent=4))
