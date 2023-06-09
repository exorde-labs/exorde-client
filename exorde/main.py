#! python3.10

import sys
import argparse
import logging, asyncio

from models import LiveConfiguration, StaticConfiguration
from faucet import faucet
from web3 import Web3
from claim_master import claim_master


async def main(command_line_arguments: argparse.Namespace):
    if not Web3.is_address(command_line_arguments.main_address):
        logging.error("The provided address is not a valid Web3 address")
        sys.exit()

    # imports are heavy and prevent an instantaneous answer to previous checks
    from spotting import spotting
    from get_live_configuration import get_live_configuration
    from get_static_configuration import get_static_configuration

    try:
        live_configuration: LiveConfiguration = await get_live_configuration()
    except:
        logging.exception(
            "An error occured retrieving live configuration, exiting"
        )
        sys.exit()
    try:
        static_configuration: StaticConfiguration = (
            await get_static_configuration(
                command_line_arguments, live_configuration
            )
        )
    except:
        logging.exception(
            "An error occured retrieving static configuration, exiting"
        )
        sys.exit()

    try:
        await claim_master(
            command_line_arguments.main_address,
            static_configuration,
            live_configuration,
        )
    except:
        logging.exception("An error occured claiming")
        sys.exit()

    for i in range(0, 3):
        try:
            await faucet(static_configuration)
            break
        except:
            logging.exception(f"An error occured during faucet (attempt {i})")
    cursor = 0
    while True:
        if cursor % 5 == 0:
            try:
                live_configuration: LiveConfiguration = (
                    await get_live_configuration()
                )
            except:
                logging.exception(
                    "An error occured retrieving the live_configuration"
                )
        cursor += 1
        if live_configuration and live_configuration["online"]:
            await spotting(live_configuration, static_configuration)
        await asyncio.sleep(live_configuration["inter_spot_delay_seconds"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main_address", help="Main wallet", type=str, required=True
    )
    command_line_arguments: argparse.Namespace = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    try:
        asyncio.run(main(command_line_arguments))
    except KeyboardInterrupt:
        logging.info("bye bye !")
