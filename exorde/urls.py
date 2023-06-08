"""URL construction define how the end-pages are going to be displayed."""

from typing import Callable
import random
import aiohttp, random
from lxml import html


async def generate_4chan_url(__keyword__: str):
    return "https://boards.4channel.org/biz/"


async def generate_reddit_url(keyword: str):
    """
    Generate a subreddit URL using the search tool with `keyword`.
    It randomly chooses one of the resulting subreddit.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://www.reddit.com/search/?q={keyword}&type=sr"
        ) as response:
            html_content = await response.text()
            tree = html.fromstring(html_content)
            urls = [
                url
                for url in tree.xpath('//a[contains(@href, "/r/")]//@href')
                if not "/r/popular" in url
            ]
            result = f"https://old.reddit.com{random.choice(urls)}new"
            return result


async def generate_twitter_url(keyword: str, live_mode=True):
    base_url = f"https://twitter.com/search?q={keyword}&src=typed_query"
    if live_mode:
        base_url = base_url + "&f=live"
    return base_url


url_generators: list[Callable] = [
    generate_twitter_url,
    generate_reddit_url,
    generate_4chan_url,
]


async def generate_url(keyword: str):
    return await random.choice(url_generators)(keyword)
