import logging
from exorde.estimate_gas import estimate_gas
import asyncio


class SpottingError(Exception):
    pass


async def spot_data(
    cid,
    item_count_,
    worker_account,
    configuration,
    gas_cache,
    contracts,
    read_web3,
    write_web3,
):
    for i in range(0, 5):
        try:
            previous_nonce = await read_web3.eth.get_transaction_count(
                worker_account.address
            )
            item_count = min(
                int(item_count_), int(configuration["batch_size"])
            )
            assert isinstance(cid, str)
            transaction = await (
                contracts["DataSpotting"]
                .functions.SpotData([cid], [""], [item_count], "")
                .build_transaction(
                    {
                        "nonce": previous_nonce,
                        "from": worker_account.address,
                        "gasPrice": configuration["default_gas_price"],
                    }
                )
            )

            estimated_transaction = await estimate_gas(
                transaction, read_web3, gas_cache, configuration
            )

            signed_transaction = read_web3.eth.account.sign_transaction(
                estimated_transaction, worker_account.key.hex()
            )
            transaction_hash = await write_web3.eth.send_raw_transaction(
                signed_transaction.rawTransaction
            )
            return transaction_hash, previous_nonce
        except Exception as e:
            # save error
            await asyncio.sleep(i * 1.5 + 1)
            logging.exception(f"An error occured during spot_data ({i}/5)")
    raise SpottingError()
