from exorde.models import LiveConfiguration, StaticConfiguration
from exorde.get_balance import get_balance
from exorde.faucet import faucet
from exorde.claim_master import claim_master

import argparse, logging, time, asyncio, os


async def verify_balance(
    static_configuration: StaticConfiguration,
    live_configuration: LiveConfiguration,
    command_line_arguments: argparse.Namespace,
):
    try:
        balance = await get_balance(static_configuration)
    except:
        balance = None
    if not balance or balance < 0.001:
        for i in range(0, 3):
            try:
                await faucet(static_configuration)
                break
            except:
                timeout = i * 1.5 + 1
                logging.exception(
                    f"An error occured during faucet (attempt {i}) (retry in {timeout})"
                )
                await asyncio.sleep(timeout)

    try:
        time.sleep(3)
        await claim_master(
            command_line_arguments.main_address,
            static_configuration,
            live_configuration,
        )
    except:
        logging.exception("An error occurred claiming Master address")
        os._exit(1)
