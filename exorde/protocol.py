import logging
import json
import os
import string
from pathlib import Path
from eth_account import Account
import random
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3 import Web3
from web3.middleware.async_cache import (
    _async_simple_cache_middleware as cache_middleware,
)
import yaml
from typing import Union
import asyncio
import aiohttp

from configuration import Configuration


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
async def get_contracts_and_abi_cnf(protocol_configuration, configuration):
    async def fetch(session, url) -> Union[tuple, dict]:
        async with session.get(url) as response:
            return await response.json(content_type=None)

    async with aiohttp.ClientSession() as session:
        requests = []
        for __name__, path in protocol_configuration["ABI"].items():
            url = f"{protocol_configuration['source']}{path}"
            request = asyncio.create_task(fetch(session, url))
            requests.append(request)
        abis = await asyncio.gather(*requests)
        contracts = dict(
            await fetch(
                session,
                f"{protocol_configuration['source']}/{protocol_configuration['contracts']}",
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


def _read_web3(protocol_configuration, network_configuration, configuration):
    return instanciate_w3(
        random.choice(  # random ip described in `urlSkale`
            random.choice(
                network_configuration[configuration["target"]]
            )[  # random target
                "urlSkale"
            ]
        )
    )


def _write_web3(protocol_configuration, network_configuration, configuration):
    return instanciate_w3(
        random.choice(network_configuration[configuration["target"]])[
            "_urlTxSkale"
        ]
    )


def contract(
    name, read_w3, contracts_and_abi, protocol_configuration, configuration
):
    abi_cnf = contracts_and_abi["abi_cnf"]
    contracts_cnf = contracts_and_abi["contracts_cnf"]
    try:
        return read_w3.eth.contract(
            contracts_cnf[configuration["target"]][name],
            abi=abi_cnf[name]["abi"],
        )
    except:
        logging.exception(f"Skipped contract instanciation for {name}")
        return None


def get_contracts(
    read_w3, contracts_and_abi, protocol_configuration, configuration
):
    return {
        name: contract(
            name,
            read_w3,
            contracts_and_abi,
            protocol_configuration,
            configuration,
        )
        for name in contracts_and_abi["contracts_cnf"][configuration["target"]]
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


async def estimate_gas(
    transaction, read_web3, gas_cache, configuration: Configuration
):
    async def do_estimate_gas():
        gas = configuration["default_gas_amount"]  # default gas amount
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


def select_random_faucet():
    private_key_base = (
        "deaddeaddeaddead5fb92d83ed54c0ea1eb74e72a84ef980d42953caaa6d"
    )
    ## faucets private keys are ["Private_key_base"+("%0.4x" % i)] with i from 0 to 499. Last 2 bytes is the selector.

    selected_faucet_index = random.randrange(
        0, 499 + 1, 1
    )  # [select index between 0 & 499 (500 faucets)]

    hex_selector_bytes = "%0.4x" % selected_faucet_index
    faucet_private_key = private_key_base + hex_selector_bytes
    return selected_faucet_index, faucet_private_key


async def faucet(
    __balance__, write_web3, read_web3, selected_faucet, worker_account
):
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


async def spot_data(
    cid,
    worker_account: Account,
    configuration,
    gas_cache,
    contracts,
    read_web3,
    write_web3,
):
    previous_nonce = await read_web3.eth.get_transaction_count(
        worker_account.address
    )
    assert isinstance(cid, str)
    transaction = await (
        contracts["DataSpotting"]
        .functions.SpotData([cid], [""], [configuration["batch_size"]], "")
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
