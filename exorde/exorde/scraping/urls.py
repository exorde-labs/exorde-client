"""URL construction define how the end-pages are going to be displayed."""

import aiohttp, random
from lxml import html


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


def generate_twitter_url(keyword, live_mode=True):
    base_url = "https://twitter.com/search?q={}&src=typed_query".format(
        str(keyword)
    )
    if live_mode:
        base_url = base_url + "&f=live"
    return base_url


__all__ = ["generate_reddit_url", "generate_twitter_url"]
