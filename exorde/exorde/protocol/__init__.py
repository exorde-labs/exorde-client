import json
from exorde.protocol.models import Batch
from madtypes import json_schema


def print_schema():
    print(json.dumps(json_schema(Batch), indent=4))


if __name__ == "__main__":
    print_schema()
