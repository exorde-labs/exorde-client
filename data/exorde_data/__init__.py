import json
from importlib import metadata
from exorde_data.models import Item

try:
    import ap98j3envoubi3fco1kc as reddit
except:
    pass


def print_schema():
    print(
        json.dumps(
            Item().json_schema(
                **{
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "$id": f'https://github.com/exorde-labs/exorde/repo/tree/v{metadata.version("exorde_data")}/exorde/schema/schema.json',
                }
            ),
            indent=4,
        )
    )
