import logging
import argparse
from typing import AsyncGenerator
from exorde.brain import think
from exorde_data import Item
from types import ModuleType
from exorde.counter import AsyncItemCounter


async def get_item(
    command_line_arguments: argparse.Namespace, counter: AsyncItemCounter
) -> AsyncGenerator[Item, None]:
    module: ModuleType
    parameters: dict
    error_count: dict[ModuleType, int] = {}
    while True:
        try:
            try:
                module, parameters, domain = await think(
                    command_line_arguments, counter
                )
            except Exception as error:
                logging.exception(f"An error occured in the brain function")
                raise error
            try:
                async for item in module.query(parameters):
                    if isinstance(item, Item):
                        await counter.increment(domain)
                        yield item
                    else:
                        continue
            except GeneratorExit:
                pass
            except Exception as e:
                logging.exception(
                    f"An error occured retrieving an item: %s using {module}",
                    e,
                )
                if not error_count[module]:
                    error_count[module] = 0
                error_count[module] += 1
        except:
            logging.exception("An error occured getting an item")
