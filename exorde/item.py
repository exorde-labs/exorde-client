import random
import logging
from typing import Callable

from typing import AsyncGenerator
from urls import generate_url

from exorde_data import query, Item

keywords = ["BTC", "MONERO", "reddit"]


def implementation(
    query: Callable[[str], AsyncGenerator[Item, None]]
) -> Callable:
    async def logic() -> AsyncGenerator[Item, None]:
        item: Item
        try:
            while True:
                try:
                    url = await generate_url(random.choice(keywords))
                    async for item in query(url):
                        if isinstance(item, Item):
                            yield item
                        else:
                            continue
                except Exception as e:
                    logging.exception("an error occured retrieving an item")
                    raise (e)
        except GeneratorExit:
            return

    return logic


get_item: Callable[[], AsyncGenerator[Item, None]] = implementation(query)
