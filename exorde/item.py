import logging
import argparse
from typing import AsyncGenerator
from exorde.brain import think
from exorde_data import Item


async def get_item(
    command_line_arguments: argparse.Namespace,
) -> AsyncGenerator[Item, None]:
    while True:
        try:
            module, parameters = await think(command_line_arguments)
            async for item in module.query(parameters):
                if isinstance(item, Item):
                    yield item
                else:
                    continue
        except Exception as e:
            logging.exception("An error occured retrieving an item: %s", e)
