#! python3.10

from wtpsplit import WtP

wtp = WtP("wtp-canine-s-1l")
import os
import argparse
import asyncio
import time
from exorde.models import LiveConfiguration, StaticConfiguration
from web3 import Web3
from exorde.claim_master import claim_master
from exorde.get_current_rep import get_current_rep
from exorde.self_update import self_update
from exorde.counter import AsyncItemCounter
from exorde.web import setup_web
from exorde.last_notification import last_notification
from exorde.docker_version_notifier import docker_version_notifier
from exorde.get_static_configuration import get_static_configuration
from exorde.get_live_configuration import get_live_configuration
from exorde.arguments import setup_arguments
from exorde.verify_balance import verify_balance

import logging


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
# logging.disable()


async def main(command_line_arguments: argparse.Namespace):
    websocket_send = await setup_web()
    counter: AsyncItemCounter = AsyncItemCounter()

    if not Web3.is_address(command_line_arguments.main_address):
        logging.error("The provided address is not a valid Web3 address")
        os._exit(1)

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

    await verify_balance(
        static_configuration, live_configuration, command_line_arguments
    )

    cursor = 1
    from exorde.spotting import spotting

    while True:
        cursor += 1
        if cursor == 10:
            cursor = 0
        if cursor % 3 == 0:
            try:
                await self_update()
            except:
                logging.info("[MAIN] An error occured during self_update")
            try:
                # update/refresh configuration
                live_configuration: LiveConfiguration = (
                    await get_live_configuration()
                )
                if live_configuration["remote_kill"] == True:
                    logging.info("Protocol is shut down (remote kill)")
                    os._exit(0)
            except:
                logging.info(
                    "[MAIN] An error occured during live configuration check."
                )
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
        await docker_version_notifier(
            live_configuration, command_line_arguments
        )
        await last_notification(live_configuration, command_line_arguments)
        if live_configuration and live_configuration["online"]:
            # quality_job = await get_available_quality_job()
            # if quality_job:
            #    quality_check(job)
            # else:
            await spotting(
                live_configuration,
                static_configuration,
                command_line_arguments,
                counter,
                websocket_send,
            )
        elif not live_configuration["online"]:
            logging.info(
                "Protocol is paused (online mode is False), temporarily. Your client will wait for the pause to end and will continue automatically."
            )
        await asyncio.sleep(live_configuration["inter_spot_delay_seconds"])


def write_env(email, password, username, http_proxy=""):
    # Check the conditions for each field
    if email is None or len(email) <= 3:
        logging.info("write_env: Invalid email. Operation aborted.")
        return
    if password is None or len(password) <= 3:
        logging.info("write_env: Invalid password. Operation aborted.")
        return
    if username is None or len(username) <= 3:
        logging.info("write_env: Invalid username. Operation aborted.")
        return

    # Define the content
    content = f"SCWEET_EMAIL={email}\nSCWEET_PASSWORD={password}\nSCWEET_USERNAME={username}\nHTTP_PROXY={http_proxy}\n"
    # Check if the .env file exists, if not create it
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(content)
        try:
            os.chmod(
                ".env", 0o600
            )  # Set file permissions to rw for the owner only
        except Exception as e:
            logging.info("Error: ", e, " - could not chmod .env, passing...")
        logging.info("write_env: .env file created.")
    else:
        with open(".env", "w") as f:
            f.write(content)
        logging.info("write_env: .env file updated.")


def clear_env():
    # Define the content
    content = (
        f"SCWEET_EMAIL=\nSCWEET_PASSWORD=\nSCWEET_USERNAME=\nHTTP_PROXY=\n"
    )
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(content)
        try:
            os.chmod(
                ".env", 0o600
            )  # Set file permissions to rw for the owner only
        except Exception as e:
            logging.info("Error: ", e, " - could not chmod .env, passing...")
        logging.info("clear_env: .env file created & cleared.")
    else:
        with open(".env", "w") as f:
            f.write(content)
        logging.info("clear_env: .env file cleared.")


def run():
    command_line_arguments = setup_arguments(write_env, clear_env)
    try:
        logging.info("Initializing exorde-client...")
        asyncio.run(main(command_line_arguments))
    except KeyboardInterrupt:
        logging.info("Exiting exorde-client...")
    except Exception:
        logging.exception("A critical error occured")


if __name__ == "__main__":
    logging.info(
        "\n*****************************\nExorde Client starting...\n*****************************\n"
    )
    run()
