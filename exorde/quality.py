
from exorde.models import LiveConfiguration, StaticConfiguration
from exorde.counter import AsyncItemCounter
import argparse
from typing import Callable
import asyncio


async def get_batch_files(static_configuration: StaticConfiguration):
    pass

async def get_last_batch_id(static_configuration: StaticConfiguration):
    contracts = static_configuration["contracts"]
    worker_address = static_configuration["worker_account"]

    # Initialize attempt counter
    attempts = 0

    while True:
        attempts += 1
        try:
            print(f"Attempt {attempts}: Fetching last batch ID...")

            # Query the contract
            last_batch_id = await contracts["DataSpotting"].functions.get_last_batch_id()

            # Successfully fetched
            print(f"Successfully fetched last batch ID: {last_batch_id}")
            return last_batch_id, attempts
        except Exception as e:
            # Log and retry
            print(f"Error fetching last batch ID: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2)


async def quality(
    live_configuration: LiveConfiguration,
    static_configuration: StaticConfiguration,
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
):
    print("Running quality")

    last_batch_id = await get_last_batch_id(static_configuration)
    print(last_batch_id)
