import aiohttp, random
from dateutil import parser
from lxml import html


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
            result = f"https://old.reddit.com{random.choice(urls)}new"
            return result


async def scrap_reddit_url(reddit_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(reddit_url) as response:
            html_content = await response.text()
            tree = html.fromstring(html_content)
            posts = tree.xpath("//div[contains(@class, 'entry')]")
            for post in posts:
                title = post.xpath("div/p/a")[0].text
                url = post.xpath("div/p/a")[0].get("href")
                url = f"https://reddit.com{url}" if url[0] == "/" else url
                username = post.xpath("div/p/a")[1].text
                time = post.xpath("div/p/time")[0].get("datetime")
                try:
                    comments = int(post.xpath("div/ul/li/a")[0].text.split(" ")[0])
                except:
                    comments = 0
                yield {
                    "entities": [],
                    "item": {
                        "Author": username,
                        "Content": "",
                        "Controversial": False,
                        "CreationDateTime": parser.parse(time).isoformat(),
                        "Description": "",
                        "DomainName": "reddit.com",
                        "Language": "en",
                        "Reference": "",
                        "Title": title,
                        "Url": url,
                        "internal_id": url,
                        "internal_parent_id": None,
                        "mediaType": "",
                        # "source": data['source'], # new
                        # "nbQuotes": data['quote_count'], # new
                        "nbComments": comments,
                        "nbLiked": 0,
                        "nbShared": 0,
                        # "isQuote": data['is_quote_status'] # new
                    },
                    "keyword": "",
                    "links": [],
                    "medias": [],
                    "spotterCountry": "",
                    "tokenOfInterest": [],
                }
