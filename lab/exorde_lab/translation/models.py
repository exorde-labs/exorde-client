from madtypes import MadType
from typing import Optional


class Translated(str, metaclass=MadType):
    description = "The content translated in English language"
    annotation = str


class Language(str, metaclass=MadType):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Translation(dict, metaclass=MadType):
    """Result of argos translate"""

    language: Optional[Language]  # uses content or title
    translation: Translated
