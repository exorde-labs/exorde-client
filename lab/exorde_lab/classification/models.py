from madtypes import Annotation, Schema

# classification: DescriptedClassification


class DescriptedClassification(tuple):
    description = "label and score of zero_shot"
    annotation = tuple[str, float]


class Classification(Schema):
    classification: DescriptedClassification
