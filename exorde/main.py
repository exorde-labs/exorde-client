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

    for i in range(0, 3):
        try:
            await faucet(static_configuration)
            break
        except:
            logging.exception(f"An error occured during faucet (attempt {i})")

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
            logging.info("Protocol is paused (online mode is False), temporarily. Your client will wait for the pause to end and will continue automatically.")
        await asyncio.sleep(live_configuration["inter_spot_delay_seconds"])

def write_env(email, password, username):
    # Check the conditions for each field
    if email is None or len(email) <= 3:
        print("Invalid email. Operation aborted.")
        return
    if password is None or len(password) <= 3:
        print("Invalid password. Operation aborted.")
        return
    if username is None or len(username) <= 3:
        print("Invalid username. Operation aborted.")
        return

    # Define the content
    content = f"SCWEET_EMAIL={email}\nSCWEET_PASSWORD={password}\nSCWEET_USERNAME={username}\n"

    # Check if the .env file exists, if not create it
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(content)
        try:
            os.chmod('.env', 0o600)  # Set file permissions to rw for the owner only
        except Exception as e:
            print("Error: ",e, " - could not chmod .env, passing...")
        print(".env file created.")
    else:
        with open('.env', 'a') as f:
            f.write(content)
        print(".env file updated.")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main_address", help="Main wallet", type=str, required=True
    )
    parser.add_argument("--twitter_username", help="Twitter username", type=str)
    parser.add_argument("--twitter_password", help="Twitter password", type=str)
    parser.add_argument("--twitter_email", help="Twitter email", type=str)

    args = parser.parse_args()

    # Check that either all or none of Twitter arguments are provided
    if (args.twitter_username is None) != (args.twitter_password is None) or (args.twitter_username is None) != (args.twitter_email is None):
        parser.error("--twitter_username, --twitter_password, and --twitter_email must be given together")
    else:
        print("Twitter login arguments detected")
        write_env(email=args.twitter_email, password=args.twitter_password, username=args.twitter_username)


    command_line_arguments: argparse.Namespace = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    try:
        asyncio.run(main(command_line_arguments))
    except KeyboardInterrupt:
        logging.info("bye bye !")


if __name__ == "__main__":
    run()
