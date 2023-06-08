import json
from typing import Callable, Coroutine, Optional
import logging
from functools import wraps
import aiohttp

from typing import TypedDict


class Configuration(TypedDict):
    online: bool
    batch_size: int
    last_info: Optional[str]
    worker_version: Optional[str]
    protocol_version: Optional[str]
    expiration_delta: Optional[int]  # data freshness
    inter_spot_delay_seconds: Optional[int]
    target: Optional[str]
    default_gas_price: Optional[int]
    default_gas_amount: Optional[int]
    gas_cap_min: Optional[int]
    inter_spot_delay_seconds: int


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
