import logging
import json
import os
import string
from pathlib import Path
from eth_account import Account
import random
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.middleware.async_cache import (
    _async_simple_cache_middleware as cache_middleware,
)
import yaml
from typing import Union
import asyncio
import aiohttp


def load_yaml(path) -> dict:
    with open(path, "r") as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data


def get_protocol_configuration() -> dict:
    return load_yaml(
        os.path.dirname(os.path.abspath(__file__))
        + "/protocol-configuration.yaml"
    )


# cnf stands for configuration
# Data-coupling because contract instanciation requires Contract & ABIS
async def get_contracts_and_abi_cnf(configuration):
    async def fetch(session, url) -> Union[tuple, dict]:
        async with session.get(url) as response:
            return await response.json(content_type=None)

    async with aiohttp.ClientSession() as session:
        requests = []
        for __name__, path in configuration["ABI"].items():
            url = f"{configuration['source']}{path}"
            request = asyncio.create_task(fetch(session, url))
            requests.append(request)
        abis = await asyncio.gather(*requests)
        contracts = dict(
            await fetch(  # casted to dict for the IDEs
                session,
                f"{configuration['source']}/{configuration['contracts']}",
            )
        )
    logging.debug(
        "abis loaded are : %s",
        ", ".join([abi["contractName"] for abi in abis]),
    )
    return {
        "contracts_cnf": contracts,
        "abi_cnf": {abi["contractName"]: abi for abi in abis},
    }


async def get_network_configuration() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/NetworkConfig.json"
        ) as response:
            json_content = await response.text()
            return json.loads(json_content)


def instanciate_w3(url):
    w3_instance = AsyncWeb3(AsyncHTTPProvider(url))
    w3_instance.middleware_onion.add(cache_middleware)
    return w3_instance


def read_web3(configuration, network_configuration):
    return instanciate_w3(
        random.choice(  # random ip described in `urlSkale`
            random.choice(
                network_configuration[configuration["target"]]
            )[  # random target
                "urlSkale"
            ]
        )
    )


def write_web3(configuration, network_configuration):
    return instanciate_w3(
        random.choice(network_configuration[configuration["target"]])[
            "_urlTxSkale"
        ]
    )


def contract(name, read_w3, abi_cnf, contracts_cnf, configuration):
    try:
        return read_w3.eth.contract(
            contracts_cnf()[configuration["target"]][name],
            abi=abi_cnf()[name]["abi"],
        )
    except:
        logging.debug("Skipped contract instanciation for %s", name)
        return None


def get_contracts(read_w3, abi_cnf, contracts_cnf, configuration):
    return {
        name: contract(name, read_w3, abi_cnf, contracts_cnf, configuration)
        for name in contracts_cnf()[configuration["target"]]
    }


def get_worker_account(worker_name: str) -> Account:
    """Return a worker key based on a name, key stored in .config"""
    keys_file = Path.home() / ".config" / "exorde" / f"{worker_name}.json"
    if keys_file.exists():
        with open(keys_file, "r") as f:
            keys = json.load(f)
            logging.debug('Loaded key "%s" from file', keys["address"])
            return Account.from_key(keys["privateKey"])

    # Generate new keys if the file does not exist
    random.seed(random.random())
    base_seed = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=256)
    )
    acct: Account = Account.create(base_seed)

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


async def get_transaction_receipt(
    transaction_hash, previous_nonce, worker_address
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
            worker_address
        )
        if current_nounce > previous_nonce:
            # found a new transaction because account nounce has increased
            break

    transaction_receipt = await read_web3.eth.wait_for_transaction_receipt(
        transaction_hash, timeout=120, poll_latency=20
    )
    return transaction_receipt


async def spot_data(
    cid,
    DataSpotting,
    worker_account: Account,
    read_web3,
    write_web3,
    default_gas_price,
    gas_cache,
):
    previous_nonce = read_web3.eth.get_transaction_count(worker_address)
    transaction = DataSpotting.functions.SpotData(
        [cid], ["1"], [100], ""
    ).build_transaction(
        {
            "nonce": previous_nonce,
            "from": worker_account.address,
            "gasPrice": default_gas_price,
        }
    )

    estimated_transaction = estimate_gas(transaction, read_web3, gas_cache)

    signed_transaction = read_web3.eth.account.sign_transaction(
        estimated_transaction, worker_account.key.hex()
    )
    transaction_hash = await write_web3.eth.send_raw_transaction(
        signed_transaction.rawTransaction
    )

    return transaction_hash, previous_nonce
