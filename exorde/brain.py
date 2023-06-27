import logging
import random
from exorde.get_keywords import get_keywords
from exorde.urls import generate_url


async def think():
    keywords_ = await get_keywords()
    selected_keyword = random.choice(keywords_)
    logging.info("[KEYWORDS] Selected = %s", selected_keyword)
    url = await generate_url(selected_keyword)
    return url
