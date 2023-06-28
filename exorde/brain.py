import logging
import importlib.metadata
import random
from exorde.get_keywords import get_keywords
from exorde.urls import generate_url
from exorde_data import get_scraping_module_for_url


async def think():
    keywords_ = await get_keywords()
    selected_keyword = random.choice(keywords_)
    logging.info(f"[BRAIN] Selected Keyword : {selected_keyword}")

    url = await generate_url(selected_keyword)
    module = await get_scraping_module_for_url(url)
    logging.info(f"[BRAIN] Selected URL : {url}")
    logging.info(
        f"[BRAIN] Selected Module : {module.__name__} ({importlib.metadata.version(module.__name__)})"
    )
    parameters = {}
    return url, module, parameters
