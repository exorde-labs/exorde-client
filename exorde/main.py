#! python3.10

import os
import argparse
import logging, asyncio

from exorde.models import LiveConfiguration, StaticConfiguration
from exorde.faucet import faucet
from web3 import Web3
from exorde.claim_master import claim_master
from exorde.get_current_rep import get_current_rep
from exorde.self_update import self_update
from exorde.get_balance import get_balance


async def main(command_line_arguments: argparse.Namespace):
    if not Web3.is_address(command_line_arguments.main_address):
        logging.error("The provided address is not a valid Web3 address")
        os._exit(1)

    # imports are heavy and prevent an instantaneous answer to previous checks
    from exorde.get_live_configuration import get_live_configuration

    try:
        live_configuration: LiveConfiguration = await get_live_configuration()
        if live_configuration["remote_kill"] == True:
            logging.info("Protocol is shut down")
            os._exit(0)
    except:
        logging.exception(
            "An error occured retrieving live configuration, exiting"
        )
        os._exit(1)

    from exorde.get_static_configuration import get_static_configuration

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
        os._exit(1)

    logging.info(
        f"Worker-Address is : {static_configuration['worker_account'].address}"
    )

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
                logging.exception(
                    f"An error occured during faucet (attempt {i})"
                )

    try:
        await claim_master(
            command_line_arguments.main_address,
            static_configuration,
            live_configuration,
        )
    except:
        logging.exception("An error occured claiming")
        os._exit(1)
    # print main address REP
    cursor = 1
    from exorde.spotting import spotting

    while True:
        if cursor % 4 == 0:
            try:
                await self_update()
                # update/refresh configuration
                live_configuration: LiveConfiguration = (
                    await get_live_configuration()
                )
                if live_configuration["remote_kill"] == True:
                    logging.info("Protocol is shut down (remote kill)")
                    os._exit(0)
            except:
                logging.exception(
                    "An error occured retrieving the live_configuration"
                )
                os._exit(0)
            try:
                current_reputation = await get_current_rep(
                    command_line_arguments.main_address
                )
                logging.info(
                    f"\n*********\n[REPUTATION] Current Main Address REP = {current_reputation}\n*********\n"
                )
            except:
                logging.exception(
                    "An error occured while logging the current reputation"
                )
        cursor += 1
        if live_configuration and live_configuration["online"]:
            await spotting(live_configuration, static_configuration)
        elif not live_configuration["online"]:
            logging.info(
                "Protocol is paused (online mode is False), temporarily. Your client will wait for the pause to end and will continue automatically."
            )
        await asyncio.sleep(live_configuration["inter_spot_delay_seconds"])


def run():
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


if __name__ == "__main__":
    run()
