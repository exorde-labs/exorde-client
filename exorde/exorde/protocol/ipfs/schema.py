from importlib import metadata
from enum import Enum
from jschemator import Schema
from jschemator.fields import EnumField, ArrayField
import json
from exorde_data.models import Item


class BatchKindEnum(Enum):
    SPOTTING = "SPOTTING"
    VALIDATION = "VALIDATION"


class ExordeBatch(Schema):
    items = ArrayField(Item())
    kind = EnumField(BatchKindEnum)


def print_schema():
    print(
        json.dumps(
            ExordeBatch().json_schema(
                **{
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "$id": f'https://github.com/exorde-labs/exorde/repo/tree/v{metadata.version("exorde_data")}/exorde/schema/schema.json',
                }
            ),
            indent=4,
        )
    )
