import logging
import argparse
from exorde.get_current_rep import get_current_rep


async def log_user_rep(command_line_arguments: argparse.Namespace):
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
