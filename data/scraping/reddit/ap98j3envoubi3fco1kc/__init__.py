import aiohttp
from lxml import html
from typing import AsyncGenerator
import pytz
import datetime

from exorde_data import Item


async def scrap_post(url: str) -> AsyncGenerator[Item, None]:
    resolvers = {}

    async def post(data) -> AsyncGenerator[Item, None]:
        """t3"""
        content = data["data"]
        yield Item(
            content=content["selftext"],
            author=content["author"],
            created_at=str(
                datetime.datetime.fromtimestamp(
                    content["created_utc"], pytz.timezone("UTC")
                ).isoformat()
            ),
            title=content["title"],
            domain="reddit.com",
            url=content["url"],
            internal_id=content["id"],
            nb_comments=content["num_comments"],
            nb_likes=content["ups"],
        )

    async def comment(data) -> AsyncGenerator[Item, None]:
        """t1"""
        content = data["data"]
        yield Item(
            content=content["body"],
            author=content["author"],
            created_at=str(
                datetime.datetime.fromtimestamp(
                    content["created_utc"], pytz.timezone("UTC")
                ).isoformat()
            ),
            domain="reddit.com",
            url="reddit.com" + content["permalink"],
            internal_id=content["id"],
            internal_parent_id=content["link_id"],
            nb_likes=content["ups"],
        )

    async def more(__data__):
        for __item__ in []:
            yield Item()

    async def kind(data) -> AsyncGenerator[Item, None]:
        resolver = resolvers.get(data["kind"], None)
        if not resolver:
            raise NotImplementedError(f"{data['kind']} is not implemented")
        try:
            async for item in resolver(data):
                yield item
        except Exception as err:
            raise err

    async def listing(data) -> AsyncGenerator[Item, None]:
        for item_data in data["data"]["children"]:
            async for item in kind(item_data):
                yield item

    resolvers = {"Listing": listing, "t1": comment, "t3": post, "more": more}
    async with aiohttp.ClientSession() as session:
        async with session.get(url + ".json") as response:
            [post, comments] = await response.json()
            async for result in kind(post):
                yield result
            async for commentary in kind(comments):
                yield commentary


async def scrap_subreddit(subreddit_url: str) -> AsyncGenerator[Item, None]:
    async with aiohttp.ClientSession() as session:
        async with session.get(subreddit_url) as response:
            html_content = await response.text()
            html_tree = html.fromstring(html_content)
            for post in html_tree.xpath("//div[contains(@class, 'entry')]"):
                async for item in scrap_post(
                    post.xpath("div/ul/li/a")[0].get("href")
                ):
                    yield item


async def query(url: str) -> AsyncGenerator[Item, None]:
    if "reddit.com" not in url:
        raise ValueError("Not a reddit URL")
    parameters = url.split("reddit.com")[1].split("/")[1:]
    if "comments" in parameters:
        async for result in scrap_post(url):
            yield result
    else:
        async for result in scrap_subreddit(url):
            yield result
