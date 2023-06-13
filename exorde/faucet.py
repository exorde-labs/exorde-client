import logging, os, asyncio
from web3 import Web3

from exorde.models import StaticConfiguration


async def faucet(static_configuration: StaticConfiguration):
    write_web3 = static_configuration["write_web3"]
    read_web3 = static_configuration["read_web3"]
    selected_faucet = static_configuration["selected_faucet"]
    worker_account = static_configuration["worker_account"]

    if not Web3.is_address(worker_account.address):
        logging.critical("Invalid worker address")
        os._exit(1)
    logging.info(
        f"Faucet with '{selected_faucet} and {worker_account.address}"
    )
    faucet_address = read_web3.eth.account.from_key(selected_faucet[1]).address
    previous_nounce = await read_web3.eth.get_transaction_count(faucet_address)
    signed_transaction = read_web3.eth.account.sign_transaction(
        {
            "nonce": previous_nounce,
            "gasPrice": 500_000,
            "gas": 100_000,
            "to": worker_account.address,
            "value": 50000000000000,
            "data": b"Hi Exorde!",
        },
        selected_faucet[1],
    )
    transaction_hash = await write_web3.eth.send_raw_transaction(
        signed_transaction.rawTransaction
    )

    await asyncio.sleep(3)
    logging.info("Waiting for transaction confirmation")
    for i in range(10):
        sleep_time = i * 1.5 + 1
        logging.debug(
            f"Waiting {sleep_time} seconds for faucet transaction confirmation"
        )
        await asyncio.sleep(sleep_time)
        # wait for new nounce by reading proxy
        current_nounce = await read_web3.eth.get_transaction_count(
            faucet_address
        )
        if current_nounce > previous_nounce:
            # found a new transaction because account nounce has increased
            break

    transaction_receipt = await read_web3.eth.wait_for_transaction_receipt(
        transaction_hash, timeout=120, poll_latency=20
    )
    logging.info(
        f"SFUEL funding transaction {transaction_receipt.transactionHash.hex()}"
    )
    await asyncio.sleep(1)
