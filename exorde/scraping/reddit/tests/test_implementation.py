from exorde_reddit import generate_subreddit_url, scrap_reddit_url
from exorde_schema import Item

import pytest


@pytest.mark.asyncio
async def test_generate_subreddit_url():
    keyword = "python"
    url = await generate_subreddit_url(keyword)
    assert "old" in url


@pytest.mark.asyncio
async def test_generate_scrap_reddit_url():
    url = "https://www.reddit.com/r/announcements/comments/8qfw8l/protecting_the_free_and_open_internet_european/"
    results = []
    async for result in scrap_reddit_url(url):
        # it should return Items
        assert isinstance(result, Item)
        results.append(result)
        print(result)
