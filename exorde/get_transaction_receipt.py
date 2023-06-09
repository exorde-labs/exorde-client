import logging, asyncio


async def get_transaction_receipt(
    transaction_hash, previous_nonce, worker_account, read_web3
):
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
            worker_account.address
        )
        if current_nounce > previous_nonce:
            # found a new transaction because account nounce has increased
            break

    transaction_receipt = await read_web3.eth.wait_for_transaction_receipt(
        transaction_hash, timeout=120, poll_latency=20
    )
    return transaction_receipt
