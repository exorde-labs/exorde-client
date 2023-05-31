from madtypes import Annotation, Schema

# classification: DescriptedClassification


class Topic(str, metaclass=Annotation):
    description = ""
    annotation = str


class Weight(str, metaclass=Annotation):
    description = ""
    annotation = float


class Classification(Schema):
    topic: Topic
    weight: Weight


class DescriptedClassification(list, metaclass=Annotation):
    description = "Probable categorization(s) of the post in a pre-determined set of general topics (list of objects with float associated for each topic, expressing their likelihood)"
    annotation = list[Classification]
