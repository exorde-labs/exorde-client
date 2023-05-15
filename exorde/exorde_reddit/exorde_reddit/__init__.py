import aiohttp, random
from lxml import html
from exorde_models import Item
from typing import AsyncGenerator


async def generate_subreddit_url(keyword: str):
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


# t3 -> t3['data'] (post)
# t1 -> t1['data']['replies'] -> listing (comment)
# listing -> listing['data']['children'] -> [t1, ...] | [t3, ...]


async def scrap_reddit_url(url: str) -> AsyncGenerator[Item, None]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url + ".json") as response:
            [post, comments] = await response.json()
            print(post)
            print(comments)
            item = Item()
            yield item


async def scrap_subreddit_url(subreddit_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(subreddit_url) as response:
            html_content = await response.text()
            html_tree = html.fromstring(html_content)
            for post in html_tree.xpath("//div[contains(@class, 'entry')]"):
                async for item in scrap_reddit_url(
                    post.xpath("div/p/a")[0].get("href")
                ):
                    yield item
