from madtypes import Annotation


class TopKeywords(list, metaclass=Annotation):
    description = "The main keywords extracted from the content field"
    annotation = set[str]
