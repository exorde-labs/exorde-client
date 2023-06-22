"""URL construction define how the end-pages are going to be displayed."""

import inspect
from typing import Callable
import random
import aiohttp, random
from lxml import html
import logging


async def generate_4chan_url(__keyword__: str):
    logging.info("[Pre-collect] generating 4chan target URL.")
    return "https://boards.4channel.org/biz/"


async def generate_reddit_url(keyword: str):
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


def convert_spaces_to_percent20(input_string):
    return input_string.replace(" ", "%20")


async def generate_twitter_url(keyword: str, live_mode=True):
    logging.info("[Pre-collect] generating Twitter target URL.")
    base_url = f"https://twitter.com/search?q={convert_spaces_to_percent20(keyword)}&src=typed_query"
    if live_mode:
        base_url = base_url + "&f=live"
    return base_url


import json


async def generate_multi_keyword(keyword: list[str], live_mode=True):
    return "multikeywords:" + json.dumps(
        {"keywords": keyword, "live_mode": live_mode}
    )


url_generators: list[list] = [
    [generate_twitter_url, 0, 60],
    [generate_reddit_url, 0, 35],
    [generate_4chan_url, 0, 5],
]

# Dev notes for 2.3
# The brain interface can be expressed as compositions of instructions such as
# `scrap this domain with this keywords using this module`
# Such expression contains the following parameters :
# - Domain to be used
# - Keyword to be used
# - Scraping module the be used

# Since the URL is the common web identifier, the task of the brain is also to compose
# the URLS that will be resolved with the correct resolver.

# As such, we maintain a set of instruction to generate URLS using keywords.
# However, such API require to be deterministic in order to project
# the property of decision to the brain.

# Currently we are using the `item` module with a `get_item` method which
# goal is to return the next item.

# This function is used to retrieve the keywords and generate the urls to be resolved
# by the query function, which independly choose the appropriate module to be used

# TODOS:
# - We need project a "brain" function which integrate more explicitly it's intentions
# - The get_item() function should work with the brain function in order to resolve URLS
# - The query function should be integrated into the brain, with an API that provides an ability
#   to choose the scraping module, it should be explcitily controled by the brain
# - The brain should be able to interupt the consumption of a generator

# The task has been written while implementing a multi-keyword solution for a particular scraping module
# - so each url_generator may require different parameters
# - today most requiere a `keyword: str`
# - now one of them require `keywords: list[str]`
# which he will use to build a FAKE url resolved with a module that will understand it's parameter


def generate_keyword_input(K: int, keywords: list[str]):
    if K == 1:
        return random.choice(keywords)
    else:
        result = []
        for __i__ in range(0, K):
            result.append(random.choice(keywords))
        return result


K = 4


async def generate_url(keywords):
    while True:
        random_generator, _, _ = random.choices(
            url_generators, weights=[item[2] for item in url_generators]
        )[0]
        try:
            signature = inspect.signature(random_generator)
            keyword_param = signature.parameters.get("keyword")
            if keyword_param is str:
                url = await random_generator(
                    generate_keyword_input(1, keywords)
                )
            else:
                url = await random_generator(
                    generate_keyword_input(K, keywords)
                )
            return url
        except:
            logging.exception(" [!] An error occured in generate_url [!]")
