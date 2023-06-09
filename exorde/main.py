#! python3.10

import argparse
import logging, asyncio

from get_configuration import get_configuration
from prepare_batch import prepare_batch
from process_batch import process_batch
from models import Configuration, Processed
from spot_data import spot_data

from exorde_lab.startup import lab_initialization
from ipfs import upload_to_ipfs
from faucet import faucet
from select_random_faucet import select_random_faucet
from get_contracts import get_contracts
from read_web3 import read_web3 as _read_web3
from write_web3 import write_web3 as _write_web3
from get_transaction_receipt import get_transaction_receipt
from get_worker_account import get_worker_account
from get_protocol_configuration import get_protocol_configuration
from get_contracts_and_abi_cnf import get_contracts_and_abi_cnf
from get_network_configuration import get_network_configuration


# TODO
# provide la main address
# check si elle est valide -> stop
#  -> si c'est good on claim_master


async def main(command_line_arguments):
    configuration: Configuration = await get_configuration()
    protocol_configuration: dict = get_protocol_configuration()
    network_configuration: dict = await get_network_configuration()
    contracts_and_abi = await get_contracts_and_abi_cnf(
        protocol_configuration, configuration
    )
    read_web3 = _read_web3(
        protocol_configuration, network_configuration, configuration
    )
    contracts = get_contracts(
        read_web3, contracts_and_abi, protocol_configuration, configuration
    )
    worker_account = get_worker_account("some-worker-name")
    gas_cache = {}
    write_web3 = _write_web3(
        protocol_configuration, network_configuration, configuration
    )
    lab_configuration = lab_initialization()
    selected_faucet = select_random_faucet()
    await faucet(None, write_web3, read_web3, selected_faucet, worker_account)
    logging.info("Initialization is complete")

    cursor = 0

    while True:
        cursor += 1
        if cursor % 10 == 0:
            try:
                configuration: Configuration = await get_configuration()
            except:
                logging.exception(
                    "An error occured retrieving the live-configuration"
                )
        if configuration["online"]:
            batch: list[Processed] = await prepare_batch(
                configuration["batch_size"], lab_configuration, configuration
            )
            if len(batch) != configuration["batch_size"]:
                logging.warning("Something weird is going on, batch ignored")
                continue
            try:
                logging.info("Processing batch")
                processed_batch = await process_batch(batch, lab_configuration)
            except:
                logging.exception("An error occured during batch processing")
                continue
            cid = await upload_to_ipfs(processed_batch)
            try:
                logging.info("Building a spot-data transaction")
                transaction_hash, previous_nonce = await spot_data(
                    cid,
                    worker_account,
                    configuration,
                    gas_cache,
                    contracts,
                    read_web3,
                    write_web3,
                )
            except:
                logging.exception(
                    "An error occured during transaction building"
                )
                continue
            try:
                logging.info("Looking for transaction receipt")
                await get_transaction_receipt(
                    transaction_hash, previous_nonce, worker_account, read_web3
                )
            except:
                logging.exception(
                    "An error occured during transaction validation"
                )
                continue
            logging.info(
                "+ A receipt for previous transaction has been confirmed"
            )
        await asyncio.sleep(configuration["inter_spot_delay_seconds"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main_address", help="Main wallet", type=str, required=True
    )
    command_line_arguments = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    try:
        asyncio.run(main(command_line_arguments))
    except KeyboardInterrupt:
        logging.info("bye bye !")
