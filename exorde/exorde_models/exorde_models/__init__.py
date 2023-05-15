from enum import Enum
import json

from jschemator import Schema
from jschemator.fields import (
    ArrayField,
    DateTimeField,
    EnumField,
    IntegerField,
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


class Item(Schema):
    """Posts & Comments both are independants Items"""

    content = StringField()
    author = StringField()  # sha1 du username
    # controversial = EnumField(Trivalent)
    creation_date_time = DateTimeField()
    description = StringField()
    language = StringField()  # weak, maybe enum ?
    title = StringField()
    domain = UrlField()
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


def print_schema():
    print(isinstance(Item().json_schema(), str))
    print(json.dumps(Item().json_schema(), indent=4))
