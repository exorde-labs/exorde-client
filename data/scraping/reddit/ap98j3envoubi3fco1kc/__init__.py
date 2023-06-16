import aiohttp
from lxml import html
from typing import AsyncGenerator
import datetime
from datetime import datetime as datett
from datetime import timedelta, timezone
import pytz
import hashlib

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

MAX_EXPIRATION_SECONDS = 120

def is_within_timeframe_seconds(dt_str, timeframe_sec):
    # Convert the datetime string to a datetime object
    dt = datett.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Make it aware about timezone (UTC)
    dt = dt.replace(tzinfo=timezone.utc)

    # Get the current datetime in UTC
    current_dt = datett.now(timezone.utc)

    # Calculate the time difference between the two datetimes
    time_diff = current_dt - dt

    # Check if the time difference is within the specified timeframe in seconds
    if abs(time_diff) <= timedelta(seconds=timeframe_sec):
        return True
    else:
        return False

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
                str(
                    datetime.datetime.fromtimestamp(
                        content["created_utc"]
                    ).isoformat()
                    + "Z"
                )
            ),
            title=Title(content["title"]),
            domain=Domain("reddit.com"),
            url=Url(content["url"]),
            # nb_comments=content["num_comments"],
            # nb_likes=content["ups"],
        )
        if is_within_timeframe_seconds(str(item_.created_at),MAX_EXPIRATION_SECONDS):
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
                str(
                    datetime.datetime.fromtimestamp(
                        content["created_utc"]
                    ).isoformat()
                    + "Z"
                )
            ),
            domain=Domain("reddit.com"),
            url=Url("https://reddit.com" + content["permalink"]),
            # nb_likes=content["ups"],
        )
        if is_within_timeframe_seconds(str(item_.created_at),MAX_EXPIRATION_SECONDS):
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
            html_tree = html.fromstring(html_content)
            for post in html_tree.xpath("//div[contains(@class, 'entry')]"):
                async for item in scrap_post(
                    post.xpath("div/ul/li/a")[0].get("href")
                ):
                    if is_within_timeframe_seconds(str(item.created_at),MAX_EXPIRATION_SECONDS):
                        yield item

async def query(url: str) -> AsyncGenerator[Item, None]:
    if "reddit.com" not in url:
        raise ValueError(f"Not a reddit URL {url}")
    parameters = url.split("reddit.com")[1].split("/")[1:]
    if "comments" in parameters:
        async for result in scrap_post(url):
            yield result
    else:
        async for result in scrap_subreddit(url):
            yield result
