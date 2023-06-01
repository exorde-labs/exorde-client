from madtypes import Annotation, Schema


class DescriptedTopKeywords(list, metaclass=Annotation):
    description = "The main keywords extracted from the content field"
    annotation = set[str]


class TopKeywords(Schema):
    top_keywords: DescriptedTopKeywords
