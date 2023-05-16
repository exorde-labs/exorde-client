import aiohttp, random
from lxml import html

from exorde_schema import Item

# from typing import AsyncGenerator


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


async def scrap_reddit_url(url: str):
    resolvers = {}

    async def post(data):
        """t3"""
        content = data["data"]
        yield Item(
            content=content["selftext"],
            author=content["author"],
            creation_datetime=content["created_utc"],  # todo: resolve date
            title=content["title"],
            domain="reddit.com",
            url=content["url"],
            internal_id=content["id"],
            nb_comments=content["num_comments"],
            nb_likes=content["ups"],
        )

    async def comment(data):
        """t1"""
        content = data["data"]
        yield Item(
            content=content["body"],
            author=content["author"],
            creation_datetime=content["created_utc"],  # todo: resolve date
            domain="reddit.com",
            url="reddit.com" + content["permalink"],
            internal_id=content["id"],
            internal_parent_id=content["link_id"],
            nb_likes=content["ups"],
        )

    async def more(__data__):
        for __item__ in []:
            yield Item()

    async def kind(data):
        resolver = resolvers.get(data["kind"], None)
        if not resolver:
            raise NotImplementedError(f"{data['kind']} is not implemented")
        try:
            async for item in resolver(data):
                yield item
        except Exception as err:
            raise err

    async def listing(data):
        for item_data in data["data"]["children"]:
            async for item in kind(item_data):
                yield item

    resolvers = {"Listing": listing, "t1": comment, "t3": post, "more": more}
    async with aiohttp.ClientSession() as session:
        async with session.get(url + ".json") as response:
            [post, comments] = await response.json()
            async for result in kind(post):
                yield result
            async for comment in kind(comments):
                yield comment


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
