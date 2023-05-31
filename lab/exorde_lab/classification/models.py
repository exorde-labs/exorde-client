from madtypes import Annotation, Schema

# classification: DescriptedClassification


class Classification(Schema):
    classification: tuple[str, float]
