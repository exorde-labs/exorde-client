#! python3.10

from wtpsplit import WtP

wtp = WtP("wtp-canine-s-1l")
import os
import argparse
import asyncio
from exorde.models import LiveConfiguration, StaticConfiguration
from web3 import Web3
from exorde.self_update import self_update
from exorde.counter import AsyncItemCounter
from exorde.web import setup_web
from exorde.last_notification import last_notification
from exorde.docker_version_notifier import docker_version_notifier
from exorde.get_static_configuration import get_static_configuration
from exorde.update_live_configuration import update_live_configuration
from exorde.log_user_rep import log_user_rep
from exorde.arguments import setup_arguments
from exorde.verify_balance import verify_balance

import time
import json
import logging
from typing import Callable


class JsonFormatter(logging.Formatter):
    def __init__(self, *__args__, **kwargs):
        self.host = kwargs["host"]
        self.api = kwargs["api"]

    LEVEL_MAP = {
        logging.INFO: 1,
        logging.DEBUG: 2,
        logging.ERROR: 3,
        logging.CRITICAL: 4,
    }

    def format(self, record):
        try:
            logcheck = record.logcheck
        except:
            logcheck = {}

        log_record = {
            "version": "1.1",
            "host": self.host,
            "short_message": record.getMessage()[:25] + "...",
            "full_message": record.getMessage(),
            "timestamp": time.time(),
            "level": self.LEVEL_MAP.get(record.levelno, 1),
            "line": record.lineno,
            "X-OVH-TOKEN": self.api,
            "_details": json.dumps(logcheck),
        }
        return json.dumps(log_record)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    JsonFormatter(
        host="node.exorde.dev",
        api="78268784-6006-485e-b7b4-c58d08549990",
    )
)


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, 
#    handlers=[stream_handler]
)
# logging.disable()


async def run_job(
    command_line_arguments: argparse.Namespace,
    spotting: Callable,
    live_configuration: LiveConfiguration,
    static_configuration: StaticConfiguration,
    counter: AsyncItemCounter,
    websocket_send: Callable,
) -> None:
    if live_configuration and live_configuration["online"]:
        await spotting(
            live_configuration,
            static_configuration,
            command_line_arguments,
            counter,
            websocket_send,
        )
    elif not live_configuration["online"]:
        logging.info(
            """
            Protocol is paused (online mode is False), temporarily. 
            Your client will continue automatically.
            """
        )
    await asyncio.sleep(live_configuration["inter_spot_delay_seconds"])


async def main(command_line_arguments: argparse.Namespace):
    websocket_send = await setup_web(command_line_arguments)
    counter: AsyncItemCounter = AsyncItemCounter()

    if not Web3.is_address(command_line_arguments.main_address):
        logging.error("The provided address is not a valid Web3 address")
        os._exit(1)

    live_configuration: LiveConfiguration = await update_live_configuration()

    static_configuration: StaticConfiguration = await get_static_configuration(
        command_line_arguments, live_configuration
    )
    logging.info(
        f"Worker-Address is : {static_configuration['worker_account'].address}"
    )

    await verify_balance(
        static_configuration, live_configuration, command_line_arguments
    )

    # this import takes a long time
    # it was moved down in order to preserve app reactivity at startup

    from exorde.spotting import spotting

    cursor = -1
    while True:
        cursor += 1
        if cursor == 10:
            cursor = 0
            if cursor % 3 == 0:
                await log_user_rep(command_line_arguments)
                await self_update()
                live_configuration = await update_live_configuration()
            await docker_version_notifier(
                live_configuration, command_line_arguments
            )
            await last_notification(live_configuration, command_line_arguments)
            await run_job(
                command_line_arguments,
                spotting,
                live_configuration,
                static_configuration,
                counter,
                websocket_send,
            )


def run():
    command_line_arguments = setup_arguments()
    try:
        logging.info("Initializing exorde-client...")
        asyncio.run(main(command_line_arguments))
    except KeyboardInterrupt:
        logging.info("Exiting exorde-client...")
    except Exception:
        logging.exception("A critical error occured")


if __name__ == "__main__":
    logging.info(
        "\n****************\nExorde Client starting...\n********************\n"
    )
    run()
