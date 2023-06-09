import json
from typing import Callable, Coroutine
import logging
from functools import wraps
import aiohttp

from models import Configuration


def logic(implementation: Callable) -> Callable:
    @wraps(implementation)
    async def call() -> Configuration:
        try:
            return await implementation()
        except:
            """If configuration fails we should stop the process"""
            logging.exception("An error occured retrieving the configuration.")
            return Configuration(
                online=False, batch_size=0, inter_spot_delay_seconds=60
            )

    return call


async def implementation() -> Configuration:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/runtime.json"
        ) as response:
            data = json.loads(await response.text())
            return Configuration(**data)


get_configuration: Callable[[], Coroutine[None, None, Configuration]] = logic(
    implementation
)
