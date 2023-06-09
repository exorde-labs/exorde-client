#! python3.10

import logging, asyncio

from get_configuration import get_configuration
from prepare_batch import prepare_batch
from process_batch import process_batch
from models import Configuration, Processed
from protocol import (
    spot_data,
    get_transaction_receipt,
    get_worker_account,
    get_protocol_configuration,
    get_contracts_and_abi_cnf,
    get_network_configuration,
)
from ipfs import upload_to_ipfs
from exorde_lab.startup import lab_initialization
from protocol import (
    _read_web3,
    _write_web3,
    get_contracts,
    select_random_faucet,
    faucet,
)


async def main():
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
    logging.basicConfig(level=logging.DEBUG)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("bye bye !")
