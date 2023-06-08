from madtypes import MadType
from typing import Callable, Coroutine
import logging
from functools import wraps


class Configuration(dict, metaclass=MadType):
    online: bool
    batch_size: int


def logic(implementation: Callable) -> Callable:
    @wraps(implementation)
    async def call() -> Configuration:
        try:
            return implementation()
        except:
            """If configuration fails we should stop the process"""
            logging.exception("An error occured retrieving the configuration.")
            return Configuration(online=False)

    return call


def implementation() -> Configuration:
    return Configuration(online=True, batch_size=100)


get_configuration: Callable[[], Coroutine[None, None, Configuration]] = logic(
    implementation
)
