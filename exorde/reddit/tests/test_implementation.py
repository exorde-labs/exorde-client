from exorde_reddit import generate_subreddit_url

import pytest


@pytest.mark.asyncio
async def test_generate_subreddit_url():
    keyword = "python"
    url = await generate_subreddit_url(keyword)
    print(url)
    assert "old" in url
