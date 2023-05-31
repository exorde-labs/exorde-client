from madtypes import Annotation, Schema


class DescriptedClassification(tuple, metaclass=Annotation):
    description = "label and score of zero_shot"
    annotation = tuple[str, float]


class Classification(Schema):
    classification: DescriptedClassification
