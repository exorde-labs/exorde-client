from madtypes import MadType


class Keywords(set, metaclass=MadType):
    description = "The main keywords extracted from the content field"
    annotation = set[str]


class TopKeywords(dict, metaclass=MadType):
    top_keywords: Keywords
