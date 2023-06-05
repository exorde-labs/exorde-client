from exorde_lab.keywords.models import TopKeywords
from exorde_lab.translation.models import (
    Translated,
    Language,
    Translation,
    CalmTranslation,
)
from exorde_lab.classification.models import Classification
from exorde_lab.analysis.models import Analysis

from exorde_data.models import CalmItem
from madtypes import MadType


class LabItem(CalmItem, CalmTranslation, metaclass=MadType):
    pass


__all__ = [
    "TopKeywords",
    "Translated",
    "Language",
    "Translation",
    "Analysis",
    "Classification",
]
