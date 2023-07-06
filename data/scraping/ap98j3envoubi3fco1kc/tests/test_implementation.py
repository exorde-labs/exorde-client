from ap98j3envoubi3fco1kc import query
from exorde_data.models import Item
import pytest


@pytest.mark.asyncio
async def test_query():
    url = "https://www.reddit.com/r/announcements/comments/8qfw8l/protecting_the_free_and_open_internet_european/"
    results = []
    async for result in query(url):
        assert isinstance(result, Item)
        results.append(result)
