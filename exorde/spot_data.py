import logging
from exorde.estimate_gas import estimate_gas
import asyncio
from exorde.faucet import faucet


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
    static_configuration,
):
    for i in range(0, 5):
        try:
            logging.info(f"[Spot Data] transaction attempt ({i}/5)")
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
                        "chainId": "2139927552"
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
            logging.info(f"[Spot Data] transaction sent")
            return transaction_hash, previous_nonce

        except ValueError as ve:
            if "balance is too low" in ve.args[0].get("message", ""):
                # Account balance is too low
                for i in range(0, 3):
                    try:
                        await faucet(static_configuration)
                        break
                    except:
                        timeout = i * 1.5 + 1
                        logging.exception(
                            f"An error occured during faucet (attempt {i}) (retry in {timeout})"
                        )
                        await asyncio.sleep(timeout)

        except Exception as e:
            await asyncio.sleep(i * 1.5 + 1)
            logging.exception(
                f"[Spot Data] An error occured during spot_data ({i}/5)"
            )

    raise SpottingError()
