from madtypes import MadType
from typing import Optional


class Content(str, metaclass=MadType):
    description = "Text body of the item"
    annotation = str


class Summary(str, metaclass=MadType):
    description = "Short version of the content"
    annotation = str


class Picture(str, metaclass=MadType):
    description = "Image linked to the item"
    annotation = str
    pattern = r"^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}"


class Author(str, metaclass=MadType):
    """todo : SHA1 format check ?"""

    description = "SHA1 encoding of the username assigned as creator of the item on its source platform"
    annotation = str


class CreatedAt(str, metaclass=MadType):
    description = "ISO8601/RFC3339 Date of creation of the item"
    annotation = str
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,6})?Z$"


class Title(str, metaclass=MadType):
    description = "Headline of the item"
    annotation = str


class Domain(str, metaclass=MadType):
    description = "Domain name on which the item was retrieved"
    annotation = str


class Url(str, metaclass=MadType):
    description = "Uniform-Resource-Locator"
    annotation = str
    pattern = r"^https?:\/\/[\S]{1,400}$"


class ExternalId(str, metaclass=MadType):
    description = "Identifier used by source"
    annotation = str


class ExternalParentId(str, metaclass=MadType):
    description = "Identifier of parent item, as used by source"
    annotation = str


class CalmItem(dict):
    """Created by a scraping module, it represent a post, article, comment..."""

    created_at: CreatedAt
    title: Optional[Title]  # titre obligatoire si pas de contenu
    content: Optional[Content]
    summary: Optional[Summary]  # <- description or summary available
    picture: Optional[Url]
    author: Optional[Author]
    external_id: Optional[ExternalId]
    external_parent_id: Optional[ExternalParentId]
    domain: Domain
    url: Url
    # type: Type # work in progress

    def is_valid(self, **kwargs) -> bool:
        """object is valid if we either have content or title"""
        return (
            False
            if not kwargs.get("content", None)
            and not kwargs.get("title", None)
            else True
        )


class Item(CalmItem, metaclass=MadType):
    pass
