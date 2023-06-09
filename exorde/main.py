#! python3.10

import sys
import argparse
import logging, asyncio

# TODO
# provide la main address
# check si elle est valide -> stop
#  -> si c'est good on claim_master

from models import LiveConfiguration, StaticConfiguration
from faucet import faucet


async def main(command_line_arguments: argparse.Namespace):
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

    logging.info("Importing spotting module")

    await faucet(static_configuration)
    cursor = 0
    while True:
        if cursor % 10 == 0:
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
