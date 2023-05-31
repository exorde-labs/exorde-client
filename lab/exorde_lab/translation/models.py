from madtypes import Annotation, Schema
from typing import Optional


class Translated(str, metaclass=Annotation):
    description = "The content translated in English language"
    annotation = str


class Language(str, metaclass=Annotation):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Translation(Schema):
    """Result of argos translate"""

    language: Optional[Language]  # uses content or title
    translation: Translated
