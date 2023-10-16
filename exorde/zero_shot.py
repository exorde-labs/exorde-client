from exorde_data import Item
from exorde.models import Classification, Translation


class TooBigError(Exception):
    pass


def zero_shot(
    item: Translation, lab_configuration, max_depth=None, depth=0
) -> Classification:
    return Classification(label=str(""), score=float(0)) # disabled 
