from madtypes import MadType


class DescriptedClassification(dict, metaclass=MadType):
    description = "label and score of zero_shot"
    score: float
    label: str


class Classification(dict, metaclass=MadType):
    classification: DescriptedClassification
