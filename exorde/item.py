import logging
from typing import AsyncGenerator

from exorde.brain import think
from exorde_data import Item


async def get_item() -> AsyncGenerator[Item, None]:
    while True:
        try:
            url, module, parameters = await think()
            async for item in module.query(url, parameters):
                if isinstance(item, Item):
                    yield item
                else:
                    continue
        except Exception as e:
            logging.exception("An error occured retrieving an item: %s", e)
            raise (e)
