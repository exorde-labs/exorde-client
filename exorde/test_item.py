import hashlib
import datetime
import pytest
from typing import AsyncGenerator
from exorde.item import implementation
from exorde_data.models import (
    Item,
    Content,
    Author,
    CreatedAt,
    Title,
    Domain,
    Url,
)


async def unstable_query(url: str) -> AsyncGenerator[Item, None]:
    yield "foo"
    yield Item(
        content=Content("some content"),
        author=Author(
            hashlib.sha1(bytes("username", encoding="utf-8")).hexdigest()
        ),
        created_at=CreatedAt(str(datetime.datetime.now().isoformat() + "Z")),
        title=Title("title"),
        domain=Domain("reddit.com"),
        url=Url("https://exorde.io/test"),
    )
    raise StopAsyncIteration()
    raise ValueError("An error")


@pytest.mark.asyncio
async def test_get_item_should_always_return_an_item():
    increment = 0
    async for item in implementation(unstable_query)():
        print(item)
        assert isinstance(item, Item)
        increment += 1
        if increment <= 10:
            break
    assert increment <= 10
