from madtypes import Annotation, Schema

# classification: DescriptedClassification


class Topic(str, metaclass=Annotation):
    description = ""
    annotation = str


class Weight(str, metaclass=Annotation):
    description = ""
    annotation = float


class ClassificationItem(Schema):
    topic: Topic
    weight: Weight


class Classification(Schema):
    classification: list[ClassificationItem]
