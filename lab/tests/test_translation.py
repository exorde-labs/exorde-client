import pytz
import datetime
from exorde_lab.translation import translate
from exorde_lab.translation.models import Translation
from exorde_data.models import Item, CreatedAt, Title, Content, Domain, Url

from argostranslate import translate as _translate


def test_translate():
    test_item = Item(
        created_at=CreatedAt(
            str(datetime.datetime.now(None).isoformat()) + "Z"
        ),
        title=Title("some title"),
        content=Content("Ceci est un magnifique contenu francais"),
        domain=Domain("test.local"),
        url=Url("https://exorde.network/"),
    )

    installed_languages = _translate.get_installed_languages()
    translated = translate(test_item, installed_languages)

    assert isinstance(translated, Translation)
    print(translated.translation)
    print(translated.language)
    assert translated.language == "fr"
    assert 1 == 2
