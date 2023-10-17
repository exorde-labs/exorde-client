from exorde.models import LiveConfiguration
from exorde.get_live_configuration import get_live_configuration
import os
import logging


async def update_live_configuration() -> LiveConfiguration:
    try:
        # update/refresh configuration
        live_configuration: LiveConfiguration = await get_live_configuration()
        if live_configuration["remote_kill"] == True:
            logging.info("Protocol is shut down (remote kill)")
            os._exit(0)
        return live_configuration
    except:
        logging.info(
            "[MAIN] An error occured during live configuration check."
        )
        os._exit(-1)
