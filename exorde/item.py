import logging
from typing import AsyncGenerator

from exorde.brain import think
from exorde_data import Item, query


async def get_item():
    async def logic() -> AsyncGenerator[Item, None]:
        while True:
            try:
                url = await think()
                async for item in query(url):
                    if isinstance(item, Item):
                        yield item
                    else:
                        continue
            except Exception as e:
                logging.exception("An error occured retrieving an item: %s", e)
                raise (e)

    return logic
