#! python3.10

import logging
import asyncio

from configuration import Configuration, get_configuration
from item import get_item, Item
from protocol import (
    spot_data,
    get_transaction_receipt,
    get_worker_account,
    get_protocol_configuration,
    get_contracts_and_abi_cnf,
    get_network_configuration,
)
from eth_account import Account
from ipfs import upload_to_ipfs


async def process(item: Item):
    return item


def process_batch(items: list[Item]):
    return items


async def send_to_ipfs(batch: list[Item]) -> str:
    return "some-cid"


async def prepare_batch(batch_size: int) -> list[Item]:
    batch: list[Item] = []
    generator = get_item()
    async for item in generator:
        print(item)
        processed_item = await process(item)
        batch.append(processed_item)
        if len(batch) == batch_size:
            await generator.aclose()
            return batch
    return []


async def main():
    configuration: Configuration = await get_configuration()

    protocol_configuration: dict = get_protocol_configuration()
    network_configuration: dict = await get_network_configuration()
    contracts_and_abi = await get_contracts_and_abi_cnf(protocol_configuration)
    worker_account = get_worker_account("some-worker-name")
    gas_cache = {}

    while True:
        batch: list[Item] = await prepare_batch(configuration.batch_size)
        if len(batch) != configuration.batch_size:
            logging.warning("Something weird is going on")
        processed_batch = process_batch(batch)
        cid = await upload_to_ipfs(processed_batch)
        # transaction_hash = await spot_data(
        #    cid,
        #    "DataSpotting",
        #    worker_account,
        #    read_web3,
        #    write_web3,
        #    configuration.default_gas_price,
        #    gas_cache,
        # )
        # await get_transaction_receipt(transaction_hash)


if __name__ == "__main__":
    asyncio.run(main())
