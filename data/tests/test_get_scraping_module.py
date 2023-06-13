from exorde_data import get_scraping_module, get_module_online_version
from importlib import metadata
import pytest


def test_get_scraping_module():
    reddit_module = get_scraping_module("reddit")
    print(reddit_module.__name__)
    print(metadata.version(reddit_module.__name__))


@pytest.mark.asyncio
async def test_get_scraping_module_online_version():
    reddit_version = await get_module_online_version("reddit")
    assert reddit_version == "0.0.1"
