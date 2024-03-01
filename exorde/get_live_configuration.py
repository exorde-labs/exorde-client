import json
from typing import Callable, Coroutine
import logging
from functools import wraps
import aiohttp

from exorde.models import LiveConfiguration


def logic(implementation: Callable) -> Callable:
    cache = None

    @wraps(implementation)
    async def call() -> LiveConfiguration:
        nonlocal cache

        try:
            result = await implementation()
        except:
            """If configuration fails we should stop the process"""
            logging.exception("An error occured retrieving the configuration.")
            if cache:
                result = cache
            else:
                return LiveConfiguration(
                    online=False, batch_size=0, inter_spot_delay_seconds=60
                )
        cache = result
        return result
    return call


async def implementation() -> LiveConfiguration:
    """ Retrieve the data from github | todo : retrieve from network """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/runtime.json"
        ) as response:
            data = json.loads(await response.text())
            return LiveConfiguration(**data)


get_live_configuration: Callable[
    [], Coroutine[None, None, LiveConfiguration]
] = logic(implementation)
