import pytest

from .. import scrap_reddit_url, Item


TEST_URL = "https://www.reddit.com/r/announcements/comments/7jsyqt/the_fccs_vote_was_predictably_frustrating_but/"


@pytest.mark.asyncio
async def test_scrap_reddit_url_should_only_return_items():
    async for item in scrap_reddit_url(TEST_URL):
        assert isinstance(item, Item)
