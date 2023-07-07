import json
from .models import Item

from madtypes import json_schema


def print_schema():
    schem = json_schema(
        Item,
        **{
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f'https://github.com/exorde-labs/exorde-client/repo/tree/v{metadata.version("exorde")}/exorde/schema/schema.json',
        },
    )
    try:
        print(
            json.dumps(
                schem,
                indent=4,
            )
        )
    except Exception as err:
        print(err)
        print(schem)
