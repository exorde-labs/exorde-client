from typing import Union

import os, json, sys
import logging
import asyncio
import random
import yaml
import string
import aiohttp
from pathlib import Path
from aiosow.bindings import read_only
from aiosow.autofill import autofill

from web3.middleware.async_cache import (
    _async_simple_cache_middleware as cache_middleware,
)
from eth_account import Account
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3


def check_erc_address_validity(erc_address):
    """check validity"""
    logging.info("check_erc_address_validity(%s)", erc_address)
    return Web3.is_address(erc_address)


async def check_user_address(
    main_address,
    no_main_address,
    AddressManager,
    write_web3,
    read_web3,
    worker_address,
    worker_key,
):
    if not no_main_address:
        if not main_address and not check_erc_address_validity(main_address):
            logging.info("Valid main-address is mandatory (see -h, use -m)")
            sys.exit()
        else:
            main_wallet_ = write_web3.to_checksum_address(main_address)
            nonce = await read_web3.eth.get_transaction_count(worker_address)
            transaction = await AddressManager.functions.ClaimMaster(
                main_wallet_
            ).build_transaction(
                {
                    "from": worker_address,
                    "gasPrice": 100_000,
                    "nonce": nonce,
                }
            )
            signed_transaction = read_web3.eth.account.sign_transaction(
                transaction, worker_key
            )
            transaction_hash = await write_web3.eth.send_raw_transaction(
                signed_transaction.rawTransaction
            )
            logging.info("Waiting for transaction confirmation")
            for i in range(10):
                sleep_time = i * 1.5 + 1
                logging.debug(f"Waiting {sleep_time} seconds for claim_master")
                await asyncio.sleep(sleep_time)
                # wait for new nounce by reading proxy
                current_nounce = await read_web3.eth.get_transaction_count(
                    worker_address
                )
                if current_nounce > nonce:
                    # found a new transaction because account nounce has increased
                    break
            await read_web3.eth.wait_for_transaction_receipt(
                transaction_hash, timeout=120, poll_latency=20
            )


def load_yaml(path):
    with open(path, "r") as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data


async def fetch(session, url) -> Union[tuple, dict]:
    async with session.get(url) as response:
        return await response.json(content_type=None)


async def configuration():
    return {
        "configuration": load_yaml(
            os.path.dirname(os.path.abspath(__file__)) + "/configuration.yaml"
        )
    }


# cnf stands for configuration
# Data-coupling because contract instanciation requires Contract & ABIS
async def contracts_and_abi_cnf(configuration):
    async with aiohttp.ClientSession() as session:
        requests = []
        for __name__, path in configuration["ABI"].items():
            url = f"{configuration['source']}{path}"
            request = asyncio.create_task(fetch(session, url))
            requests.append(request)
        abis = await asyncio.gather(*requests)
        contracts = dict(
            await fetch(  # casted to dict for the IDEs
                session, f"{configuration['source']}/{configuration['contracts']}"
            )
        )
    logging.debug(
        "abis loaded are : %s", ", ".join([abi["contractName"] for abi in abis])
    )
    return {
        "contracts_cnf": read_only(contracts),
        "abi_cnf": read_only({abi["contractName"]: abi for abi in abis}),
    }


def read_web3(configuration):
    return {
        "read_web3": instanciate_w3(
            random.choice(configuration[configuration["target"]]["_urlSkale"])
        )
    }


def instanciate_w3(url):
    w3_instance = AsyncWeb3(AsyncHTTPProvider(url))
    w3_instance.middleware_onion.add(cache_middleware)
    return w3_instance


def write_web3(configuration):
    return {
        "write_web3": instanciate_w3(
            configuration[configuration["target"]]["_urlTxSkale"]
        )
    }


def contract(name, read_w3, abi_cnf, contracts_cnf, configuration):
    try:
        return read_w3.eth.contract(
            contracts_cnf()[configuration["target"]][name], abi=abi_cnf()[name]["abi"]
        )
    except:
        logging.debug("Skipped contract instanciation for %s", name)
        return None


def contracts(read_w3, abi_cnf, contracts_cnf, configuration):
    try:
        return {
            name: contract(name, read_w3, abi_cnf, contracts_cnf, configuration)
            for name in contracts_cnf()[configuration["target"]]
        }
    except KeyError as e:
        logging.critical(
            "Mathias did something weird with the keys again. Please reach him on discord"
        )
        raise e


def worker_address():
    """Generates an ERC address and key"""
    keys_file = Path.home() / ".config" / "exorde" / "keys.json"
    if keys_file.exists():
        with open(keys_file, "r") as f:
            keys = json.load(f)
            logging.debug('Loaded key "%s" from file', keys["address"])
            return Account.from_key(keys["privateKey"])

    # Generate new keys if the file does not exist
    random.seed(random.random())
    base_seed = "".join(random.choices(string.ascii_uppercase + string.digits, k=256))
    acct = Account.create(base_seed)

    # Save the new keys to the file
    os.makedirs(keys_file.parent, exist_ok=True)
    with open(keys_file, "w") as f:
        keys = {
            "address": acct.address,
            "privateKey": acct.key.hex(),
        }
        json.dump(keys, f, indent=4)
        logging.debug('Saved key "%s" to file', keys["address"])

    return acct


async def log_current_rep(worker_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"
        ) as response:
            leaderboard = json.loads(await response.text())
            logging.info(
                f"Current rep = {round(leaderboard.get(worker_address, 0), 4)}"
            )


async def send_raw_transaction(transaction, write_web3, read_web3, worker_address):
    try:
        previous_nonce = await read_web3.eth.get_transaction_count(worker_address)
        transaction_hash = await write_web3.eth.send_raw_transaction(
            transaction.rawTransaction
        )
        logging.info("A transaction has been sent")
        logging.info("Waiting for transaction confirmation")
        for i in range(10):
            sleep_time = i * 1.5 + 1
            logging.debug(
                f"Waiting {sleep_time} seconds for faucet transaction confirmation"
            )
            await asyncio.sleep(sleep_time)
            # wait for new nounce by reading proxy
            current_nounce = await read_web3.eth.get_transaction_count(worker_address)
            if current_nounce > previous_nonce:
                # found a new transaction because account nounce has increased
                break
        await read_web3.eth.wait_for_transaction_receipt(
            transaction_hash, timeout=120, poll_latency=20
        )
    except Exception as e:
        logging.error(f"Error sending transaction : {e}")
        raise (e)
    logging.info("A transaction has been confirmed")
    return {"transaction": None, "current_cid_commit": None}


async def nonce(worker_address, read_web3):
    try:
        return await read_web3.eth.get_transaction_count(worker_address)
    except Exception as e:
        logging.error(f"Error getting nonce ({worker_address})")
        raise e


async def spot_data(cid, DataSpotting):
    # todo: "1" is for twitter.com, it should be specified dynamicaly
    try:
        return DataSpotting.functions.SpotData([cid], ["1"], [100], "")
    except Exception:
        logging.error("Error calling SpotData")


def sign_transaction(transaction, worker_key, read_web3):
    return read_web3.eth.account.sign_transaction(transaction, worker_key)


async def build_transaction(transaction, worker_address, nonce):
    try:
        return await transaction.build_transaction(
            {"nonce": nonce, "from": worker_address, "gasPrice": 100_000}
        )
    except Exception as e:
        logging.error("Error building transaction")
        raise (e)


async def estimate_gas(transaction, read_web3, gas_cache):
    async def do_estimate_gas():
        gas = 100_000  # default gas amount
        estimate = await read_web3.eth.estimate_gas(transaction) * 1.5
        if estimate < 100_000:
            gas = estimate + 500_000
        return max(10_000_000, gas)

    function_bytecode = str(transaction["data"])[2:10]
    data_length = len(str(transaction["data"]))
    gas_key = (function_bytecode, data_length)
    if gas_key in gas_cache:
        transaction["gas"] = gas_cache[gas_key]
    else:
        estimate = await do_estimate_gas()
        gas_cache[gas_key] = estimate
        transaction["gas"] = gas_cache[gas_key]
    return transaction


async def register(
    DataSpotting, worker_address, worker_key, nonce, write_web3, read_web3
):
    """register contains the full transaction in order to block the setup."""
    try:
        transaction = await build_transaction(
            DataSpotting.functions.RegisterWorker(), worker_address, nonce
        )
        signed_transaction = sign_transaction(transaction, worker_key, read_web3)
        await send_raw_transaction(
            signed_transaction, write_web3, read_web3, worker_address
        )
        return {"worker_registered": True}
    except Exception as error:
        logging.error(error)
        return {"worker_registered": True}


async def is_new_work_available(worker_address, DataSpotting) -> bool:
    try:
        result = await DataSpotting.functions.IsNewWorkAvailable(worker_address).call()
    except:
        result = False
    return result


async def get_current_work(worker_address, DataSpotting) -> int:  # returns batch_id
    logging.info("get_current_work [%s, %s]", worker_address, DataSpotting)
    result = await DataSpotting.functions.GetCurrentWork(worker_address).call()
    return result


async def get_ipfs_hashes_for_batch(batch_id, DataSpotting) -> list:
    """Return la list cid associe au batch_id"""
    return await DataSpotting.functions.getIPFShashesForBatch(int(batch_id)).call()


async def is_worker_allocated_to_batch(batch_id, worker_address, DataSpotting):
    return await DataSpotting.functions.isWorkerAllocatedToBatch(
        batch_id, worker_address
    ).call()


async def did_commit(batch_id, worker_address, DataSpotting):
    return await DataSpotting.functions.didCommit(worker_address, batch_id).call()


def random_seed():
    return random.randint(0, 999999999)


async def get_encrypted_string_hash(file_cid, seed, DataSpotting):
    return await DataSpotting.functions.getEncryptedStringHash(file_cid, seed).call()


async def get_encrypted_hash(vote: int, seed, DataSpotting):
    return await DataSpotting.functions.getEncryptedHash(vote, seed).call()


async def commit_spot_check(
    batch_id, file_cid, vote, batch_length: int, DataSpotting, memory
):
    seed = random_seed()
    encrypted_string_hash = await autofill(
        get_encrypted_string_hash, args=[file_cid, seed], memory=memory
    )
    encrypted_hash = await autofill(
        get_encrypted_hash, args=[vote, seed], memory=memory
    )
    return (
        await DataSpotting.functions.commit_spot_check(
            batch_id, encrypted_string_hash, encrypted_hash, batch_length, 1
        ),
        seed,
    )


# use the same random seed for commit and reveal


async def is_commit_period_active(batch_id, DataSpotting):
    return await DataSpotting.functions.commitPeriodActive(batch_id).call()


async def is_commit_period_over(batch_id, DataSpotting):
    return await DataSpotting.functions.commitPeriodOver(batch_id).call()


async def is_reveal_period_active(batch_id, DataSpotting):
    return await DataSpotting.functions.revealPeriodActive(batch_id).call()


async def is_reveal_period_over(batch_id, DataSpotting):
    return await DataSpotting.functions.revealPeriodOver(batch_id).call()


async def reveal_spot_check(batch_id, file_cid, vote, seed, DataSpotting):
    return await DataSpotting.revealSpotCheck(batch_id, file_cid, vote, seed).call()


async def remaining_commit_duration(batch_id, DataSpotting):
    return await DataSpotting.functions.remainingCommitDuration(batch_id).call()


async def remaining_reveal_duration(batch_id, DataSpotting):
    return await DataSpotting.functions.remainingRevealDuration(batch_id).call()


async def init_gas_cache():
    return {"gas_cache": {}}


async def get_balance(read_web3, worker_address):
    try:
        return await read_web3.eth.get_balance(worker_address)
    except Exception as e:
        logging.error(e)
        return 0


def select_random_faucet():
    private_key_base = "deaddeaddeaddead5fb92d83ed54c0ea1eb74e72a84ef980d42953caaa6d"
    ## faucets private keys are ["Private_key_base"+("%0.4x" % i)] with i from 0 to 499. Last 2 bytes is the selector.

    selected_faucet_index = random.randrange(
        0, 499 + 1, 1
    )  # [select index between 0 & 499 (500 faucets)]

    hex_selector_bytes = "%0.4x" % selected_faucet_index
    faucet_private_key = private_key_base + hex_selector_bytes
    return selected_faucet_index, faucet_private_key


async def faucet(__balance__, write_web3, read_web3, selected_faucet, worker_address):
    if not Web3.is_address(worker_address):
        logging.critical("Invalid worker address")
        os._exit(1)
    logging.info(f"Faucet with '{selected_faucet} and {worker_address}")
    faucet_address = read_web3.eth.account.from_key(selected_faucet[1]).address
    previous_nounce = await read_web3.eth.get_transaction_count(faucet_address)
    signed_transaction = read_web3.eth.account.sign_transaction(
        {
            "nonce": previous_nounce,
            "gasPrice": 500_000,
            "gas": 100_000,
            "to": worker_address,
            "value": 500000000000000,
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
        current_nounce = await read_web3.eth.get_transaction_count(faucet_address)
        if current_nounce > previous_nounce:
            # found a new transaction because account nounce has increased
            break

    transaction_receipt = await read_web3.eth.wait_for_transaction_receipt(
        transaction_hash, timeout=120, poll_latency=20
    )
    logging.info(
        f"SFUEL funding transaction {transaction_receipt.transactionHash.hex()}"
    )
