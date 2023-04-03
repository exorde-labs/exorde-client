import logging
from argostranslate import package
from ftlangdetect import detect as _detect
from typing import cast


def install_translation_modules():
    """Download and install Argos Translate translation packages"""
    package.update_package_index()
    available_packages = package.get_available_packages()
    length = len(available_packages)
    logging.info(f"{length} translation modules to install")
    i = 0
    for pkg in available_packages:
        i += 1
        logging.info(f" - installing translation module ({i}/{length}) : ({str(pkg)})")

        # cast used until this is merged https://github.com/argosopentech/argos-translate/pull/329
        package.install_from_path(cast(package.AvailablePackage, pkg).download())


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


def translate(item, low_memory, installed_languages):
    text = item["item"]["Content"]
    language = _detect(text, low_memory)
    try:
        item["item"]["Content"] = translation(
            language["lang"], "en", installed_languages
        ).translate(text)
    except:
        logging.error(
            f"Error translating from {language['lang']} ({item['item']['internal_id']})"
        )
    return item
