from madtypes import MadType


class DescriptedClassification(tuple, metaclass=MadType):
    description = "label and score of zero_shot"
    annotation = tuple[str, float]


class Classification(dict, metaclass=MadType):
    classification: DescriptedClassification
