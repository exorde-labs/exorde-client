from ch4875eda56be56000ac import query
from exorde_data.models import Item
import pytest


@pytest.mark.asyncio
async def test_query():
    url = "https://boards.4channel.org/biz/"
    results = []
    async for result in query(url):
        assert isinstance(result, Item)
        results.append(result)
