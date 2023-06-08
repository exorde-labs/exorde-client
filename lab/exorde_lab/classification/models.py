from madtypes import MadType


class Classification(dict, metaclass=MadType):
    description = "label and score of zero_shot"
    score: float
    label: str
