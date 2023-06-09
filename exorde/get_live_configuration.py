import json
from typing import Callable, Coroutine
import logging
from functools import wraps
import aiohttp

from models import LiveConfiguration


def logic(implementation: Callable) -> Callable:
    @wraps(implementation)
    async def call() -> LiveConfiguration:
        try:
            return await implementation()
        except:
            """If configuration fails we should stop the process"""
            logging.exception("An error occured retrieving the configuration.")
            return LiveConfiguration(
                online=False, batch_size=0, inter_spot_delay_seconds=60
            )

    return call


async def implementation() -> LiveConfiguration:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/runtime.json"
        ) as response:
            data = json.loads(await response.text())
            return LiveConfiguration(**data)


get_live_configuration: Callable[
    [], Coroutine[None, None, LiveConfiguration]
] = logic(implementation)
