import pytz
import datetime
from exorde_lab.translation import translate
from exorde_data.models import Item, CreatedAt, Title, Content, Domain, Url


def test_translate():
    test_item = Item(
        created_at=CreatedAt(
            str(datetime.datetime.now(None).isoformat()) + "Z"
        ),
        title=Title("some title"),
        content=Content("some content"),
        domain=Domain("test.local"),
        url=Url("https://test.local/fake/item"),
    )
