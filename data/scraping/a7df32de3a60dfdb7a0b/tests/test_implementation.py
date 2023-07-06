from a7df32de3a60dfdb7a0b import query
from exorde_data.models import Item
import pytest


@pytest.mark.asyncio
async def test_query():
    url = "https://twitter.com/search?q=financial&src=typed_query&f=live"
    results = []
    async for result in query(url):
        assert isinstance(result, Item)
        results.append(result)
