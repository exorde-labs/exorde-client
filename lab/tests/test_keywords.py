import datetime
from exorde_lab.translation import translate
from exorde_lab.translation.models import Translation
from exorde_data.models import Item, CreatedAt, Title, Content, Domain, Url
from exorde_lab.keywords import populate_keywords

from argostranslate import translate as _translate


def test_keyword_extraction():
    test_item = Item(
        created_at=CreatedAt(
            str(datetime.datetime.now(None).isoformat()) + "Z"
        ),
        title=Title("some title"),
        content=Content("Bitcoin is having a great time" ""),
        domain=Domain("test.local"),
        url=Url("https://exorde.network/"),
    )

    installed_languages = _translate.get_installed_languages()
    translated = translate(test_item, installed_languages)

    assert isinstance(translated, Translation)
    print(translated.translation)
    print(translated.language)
    assert translated.language == "en"
    top_keywords = populate_keywords(translated)
    assert top_keywords.top_keywords == {
        "great time",
        "Bitcoin",
        "great",
        "time",
    }
