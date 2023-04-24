from aiosow.bindings import setup, alias
import aiohttp, random
from lxml import html


@setup
def set_keyword():
    return {"keyword": "BTC"}


@setup
async def generate_reddit_url(keyword):
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
            result = f"https://www.reddit.com{random.choice(urls)}"
            return result


async def scrap_reddit_url(reddit_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(reddit_url) as response:
            html_content = await response.text()
            tree = html.fromstring(html_content)
