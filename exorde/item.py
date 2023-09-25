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
import hashlib


def create_exception_identifier(traceback_list: list[str]) -> str:
    # Concatenate the list of strings into a single string
    traceback_str = "\n".join(traceback_list)

    # Create a hashlib object (SHA-256 in this example, but you can choose other hash algorithms)
    hasher = hashlib.sha256()

    # Update the hash object with the traceback string
    hasher.update(traceback_str.encode("utf-8"))

    # Get the hexadecimal representation of the hash
    exception_identifier = hasher.hexdigest()

    return exception_identifier


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
                            intent_id: {"module": module.__name__},
                        },
                        "modules": {module.__name__: {}},
                    }
                )

            except Exception as error:
                await websocket_send(
                    {"intents": {intent_id: {"error": str(error)}}}
                )
                logging.exception(f"An error occured in the brain function")
                raise error
            collection_id = str(uuid.uuid4())
            try:
                async for item in module.query(parameters):
                    await websocket_send(
                        {
                            "intents": {
                                intent_id: {
                                    "collections": {
                                        collection_id: {
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
            except Exception as e:
                # Retrieve and format the traceback as a list of strings
                traceback_list = traceback.format_exception(
                    type(e), e, e.__traceback__
                )
                error_id = create_exception_identifier(traceback_list)

                await websocket_send(
                    {
                        "intents": {intent_id: {"errors": error_id}},
                        "errors": {
                            error_id: {
                                "traceback": traceback_list,
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
