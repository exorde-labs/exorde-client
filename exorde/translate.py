import logging
from ftlangdetect import detect as _detect
from models import Translation, Language, Translated, Item


from_lang = lambda from_code, installed_languages: list(
    filter(lambda x: x.code == from_code, installed_languages)
)[0]
to_lang = lambda to_code, installed_languages: list(
    filter(lambda x: x.code == to_code, installed_languages)
)[0]
translation = lambda from_code, to_code, installed_languages: from_lang(
    from_code, installed_languages
).get_translation(to_lang(to_code, installed_languages))

detect = lambda text, low_memory: _detect(text, low_memory=low_memory)


def translate(
    item: Item, installed_languages, low_memory: bool = False
) -> Translation:
    text = str(item.content if item.content else item.title)
    language = _detect(text, low_memory)
    try:
        if language["lang"] != "en":
            translated = translation(
                language["lang"], "en", installed_languages
            ).translate(text)
        else:
            translated = item.content
        return Translation(
            language=Language(language["lang"]),
            translation=Translated(translated),
        )
    except Exception as err:
        logging.error(
            f"Error translating from {language['lang']} ({item}) : {err}"
        )
        return Translation(
            language=Language(language["lang"]),
            translation=Translated(item.content),
        )
