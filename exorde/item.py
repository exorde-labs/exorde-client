import asyncio
import logging
from typing import Callable
from madtypes import MadType

from typing import AsyncGenerator


class Item(dict, metaclass=MadType):
    content: str


def generate_url() -> str:
    return "http://an-url.com"


def implementation(
    query: Callable[[str], AsyncGenerator[Item, None]]
) -> Callable:
    async def logic() -> AsyncGenerator[Item, None]:
        item: Item
        try:
            while True:
                try:
                    async for item in query(generate_url()):
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


async def query(__url__: str):
    for i in range(10):
        await asyncio.sleep(1)  # Delay of 1 second between iterations
        yield Item(content=str(i))


get_item: Callable[[], AsyncGenerator[Item, None]] = implementation(query)
