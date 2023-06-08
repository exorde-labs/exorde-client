from madtypes import MadType


class Keywords(list, metaclass=MadType):
    description = "The main keywords extracted from the content field"
    annotation = list[str]


class TopKeywords(dict, metaclass=MadType):
    top_keywords: Keywords
