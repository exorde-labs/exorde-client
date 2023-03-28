from aiosow.bindings import setup, wrap, option, wire
from argostranslate import translate as _translate
from . import install_translation_modules, translate as translate_implementation

get_installed_languages = wrap(lambda result: {"installed_languages": result})(
    _translate.get_installed_languages
)
option(
    "low_memory",
    action="store_true",
    default=False,
    help="Enables translation language predictions with the compressed version of the fasttext model.",
)


# from . import install_translation_modules
# setup(install_translation_modules)  # should be triggered if installed_languages == []
setup(get_installed_languages)

on_content_to_translate_do, on_translated_do = wire()
translate = on_content_to_translate_do(translate_implementation)
# translatedText = translate('Hello World')
