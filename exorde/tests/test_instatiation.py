from datetime import datetime
from exorde.protocol.models import ProtocolItem
from exorde_data.models import Title, CreatedAt, Domain, Url
from exorde_lab.translation.models import Language


def test_create_protocol_item():
    print(">>>", ProtocolItem.get_fields())
    ProtocolItem(
        title=Title("foo"),
        created_at=CreatedAt(datetime.now().isoformat() + "Z"),
        domain=Domain("exorde.io"),
        url=Url("https://exorde.io/some-test"),
        langage=Language("fr"),
    )
