import logging
import argparse
from typing import AsyncGenerator
from exorde.brain import think
from exorde_data import Item
from types import ModuleType
from exorde.counter import AsyncItemCounter
from typing import Callable
import uuid
from datetime import datetime
import traceback
from exorde.create_error_identifier import create_error_identifier
from exorde.get_module_version import get_module_version


async def choose_module(
    command_line_arguments, counter, websocket_send, intent_id
):
    try:
        module, parameters, domain = await think(
            command_line_arguments, counter, websocket_send, intent_id
        )
        await websocket_send(
            {
                "intents": {
                    intent_id: {
                        "module": module.__name__,
                        "parameters": parameters,
                    },
                },
                "modules": {
                    module.__name__: {
                        "version": get_module_version(module.__name__),
                        "intents": {intent_id: {"parameters": parameters}},
                    }
                },
            }
        )
        return (module, parameters, domain)

    except Exception as error:
        await websocket_send({"intents": {intent_id: {"error": str(error)}}})
        logging.exception(f"An error occured in the brain function")
        raise error


async def get_item(
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
) -> AsyncGenerator[Item, None]:
    """
    1. Retrieve module & domain using `brain.think`
    2. Use module.query AsyncGenerator to retrieve items
    """
    module: ModuleType
    parameters: dict
    error_count: dict[ModuleType, int] = {}
    while True:
        try:
            intent_id = str(uuid.uuid4())

            await websocket_send(
                {
                    "intents": {
                        intent_id: {
                            "start": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    }
                }
            )
            (module, parameters, domain) = await choose_module(
                command_line_arguments, counter, websocket_send, intent_id
            )

            try:
                async for item in module.query(parameters):
                    if isinstance(item, Item):
                        await websocket_send(
                            {
                                "intents": {
                                    intent_id: {
                                        "collections": {
                                            str(uuid.uuid4()): {
                                                "url": str(item.url),
                                                "end": datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                ),
                                            }
                                        }
                                    }
                                }
                            }
                        )
                        await counter.increment(domain)
                        yield item
                    else:
                        continue
            except GeneratorExit:
                pass
            except Exception as e:
                traceback_list = traceback.format_exception(
                    type(e), e, e.__traceback__
                )
                error_id = create_error_identifier(traceback_list)
                await websocket_send(
                    {
                        "intents": {intent_id: {"errors": {error_id: {}}}},
                        "modules": {
                            module.__name__: {"errors": {error_id: {}}}
                        },
                        "errors": {
                            error_id: {
                                "traceback": traceback_list,
                                "module": module.__name__,
                                "intents": {
                                    intent_id: {
                                        datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ): {}
                                    }
                                },
                            }
                        },
                    }
                )
                logging.exception(
                    f"An error occured retrieving an item: %s using {module}",
                    e,
                )
                if not error_count[module]:
                    error_count[module] = 0
                error_count[module] += 1
        except:
            logging.exception("An error occured getting an item")
