import random
import aiohttp
from lxml import html
from typing import AsyncGenerator
import datetime
import time
from datetime import datetime as datett
from datetime import timezone
import pytz
import hashlib
import logging
from lxml.html import fromstring

from exorde_data import (
    Item,
    Content,
    Author,
    CreatedAt,
    Title,
    Url,
    Domain,
)

import hashlib

MAX_EXPIRATION_SECONDS = 180


async def generate_url(keyword: str = "BTC"):
    """
    Generate a subreddit URL using the search tool with `keyword`.
    It randomly chooses one of the resulting subreddit.
    """
    logging.info("[Pre-collect] generating Reddit target URL.")
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


def is_within_timeframe_seconds(input_timestamp, timeframe_sec):
    input_timestamp = int(input_timestamp)
    current_timestamp = int(time.time())  # Get the current UNIX timestamp
    elapsed_time = current_timestamp - input_timestamp

    if elapsed_time <= timeframe_sec:
        return True
    else:
        return False


def format_timestamp(timestamp):
    dt = datett.fromtimestamp(timestamp, timezone.utc)
    formatted_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_timestamp


async def scrap_post(url: str) -> AsyncGenerator[Item, None]:
    resolvers = {}

    async def post(data) -> AsyncGenerator[Item, None]:
        """t3"""
        content = data["data"]
        item_ = Item(
            content=Content(content["selftext"]),
            author=Author(
                hashlib.sha1(
                    bytes(content["author"], encoding="utf-8")
                ).hexdigest()
            ),
            created_at=CreatedAt(
                str(format_timestamp(content["created_utc"]))
            ),
            title=Title(content["title"]),
            domain=Domain("reddit.com"),
            url=Url(content["url"]),
        )
        if is_within_timeframe_seconds(
            content["created_utc"], MAX_EXPIRATION_SECONDS
        ):
            yield item_

    async def comment(data) -> AsyncGenerator[Item, None]:
        """t1"""
        content = data["data"]
        item_ = Item(
            content=Content(content["body"]),
            author=Author(
                hashlib.sha1(
                    bytes(content["author"], encoding="utf-8")
                ).hexdigest()
            ),
            created_at=CreatedAt(
                str(format_timestamp(content["created_utc"]))
            ),
            domain=Domain("reddit.com"),
            url=Url("https://reddit.com" + content["permalink"]),
        )
        if is_within_timeframe_seconds(
            content["created_utc"], MAX_EXPIRATION_SECONDS
        ):
            yield item_

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
            html_tree = fromstring(html_content)
            for post in html_tree.xpath("//div[contains(@class, 'entry')]"):
                async for item in scrap_post(
                    post.xpath("div/ul/li/a")[0].get("href")
                ):
                    yield item


async def query(parameters: dict) -> AsyncGenerator[Item, None]:
    url = await generate_url(**parameters["url_parameters"])
    logging.info("[Reddit] Scraping %s", url)
    if "reddit.com" not in url:
        raise ValueError(f"Not a reddit URL {url}")
    url_parameters = url.split("reddit.com")[1].split("/")[1:]
    if "comments" in url_parameters:
        async for result in scrap_post(url):
            logging.info("[Reddit] found post = %s", result)
            yield result
    else:
        async for result in scrap_subreddit(url):
            logging.info("[Reddit] found post = %s", result)
            yield result
