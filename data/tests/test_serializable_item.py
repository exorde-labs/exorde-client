import json
from exorde_data.models import Item


def test_wether_item_is_jsonable():
    arr = [Item(content="Foo"), Item(content="Bar")]
    assert json.loads(json.dumps(arr)) == arr
    print(json.dumps(arr, indent=4), arr)
