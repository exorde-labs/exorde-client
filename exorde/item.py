import logging
import asyncio
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
import pkg_resources
from exorde.create_error_identifier import create_error_identifier


def get_module_version(module_name):
    try:
        # Use pkg_resources to retrieve the distribution object for the module
        distribution = pkg_resources.get_distribution(module_name)

        # Get the version from the distribution object
        module_version = distribution.version

        return module_version
    except Exception as e:
        return f"Unable to retrieve version for {module_name}: {str(e)}"


async def get_item(
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
) -> AsyncGenerator[Item, None]:
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

            try:
                module, parameters, domain = await think(
                    command_line_arguments, counter, websocket_send
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
                                "intents": {
                                    intent_id: {"parameters": parameters}
                                },
                            }
                        },
                    }
                )

            except Exception as error:
                await websocket_send(
                    {"intents": {intent_id: {"error": str(error)}}}
                )
                logging.exception(f"An error occured in the brain function")
                raise error

            try:
                async for item in module.query(parameters):
                    await websocket_send(
                        {
                            "intents": {
                                intent_id: {
                                    "collections": {
                                        str(uuid.uuid4()): {
                                            "url": item.url,
                                            "end": datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            ),
                                        }
                                    }
                                }
                            }
                        }
                    )
                    if isinstance(item, Item):
                        await counter.increment(domain)
                        yield item
                    else:
                        continue
            except GeneratorExit:
                pass
            except Exception as e:
                # Retrieve and format the traceback as a list of strings
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
