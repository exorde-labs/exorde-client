import random
import logging
from typing import Callable
from typing import AsyncGenerator
from exorde.urls import generate_url

from exorde_data import query, Item

from exorde.get_keywords import get_keywords


def implementation(
    query: Callable[[str], AsyncGenerator[Item, None]]
) -> Callable:
    async def logic() -> AsyncGenerator[Item, None]:
        item: Item
        while True:
            try:
                keywords_ = await get_keywords()
                selected_keyword = random.choice(keywords_)
                logging.info("[KEYWORDS] Selected = %s", selected_keyword)
                url = await generate_url(selected_keyword)
                async for item in query(url):
                    if isinstance(item, Item):
                        yield item
                    else:
                        continue
            except Exception as e:
                logging.exception("An error occured retrieving an item: %s", e)
                raise (e)

    return logic


get_item: Callable[[], AsyncGenerator[Item, None]] = implementation(query)
