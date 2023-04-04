from typing import Union

import os
import logging
import asyncio
import random
from ens.async_ens import default
import yaml
import string
import aiohttp
from aiosow.bindings import read_only

from web3.middleware.async_cache import (
    _async_simple_cache_middleware as cache_middleware,
)
from eth_account import Account
from web3 import AsyncWeb3, AsyncHTTPProvider


def load_yaml(path):
    with open(path, "r") as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data


async def fetch(session, url) -> Union[tuple, dict]:
    async with session.get(url) as response:
        return await response.json(content_type=None)


configuration = lambda: {
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
    logging.info(
        "abis loaded are : %s", ", ".join([abi["contractName"] for abi in abis])
    )
    return {
        "contracts_cnf": read_only(contracts),
        "abi_cnf": read_only({abi["contractName"]: abi for abi in abis}),
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


def read_web3(configuration):
    return {
        "read_web3": instanciate_w3(
            random.choice(configuration[configuration["target"]]["_urlSkale"])
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
    return {
        name: contract(name, read_w3, abi_cnf, contracts_cnf, configuration)
        for name in contracts_cnf()[configuration["target"]]
    }


def worker_address():
    """Generates an ERC address and key"""
    random.seed(random.random())
    base_seed = "".join(random.choices(string.ascii_uppercase + string.digits, k=256))
    acct = Account.create(base_seed)
    logging.debug('Generated a key "%s"', acct.address)
    return acct


def worker_addresses(workers):
    return {
        "worker_addresses": {
            addr: key for addr, key in (worker_address() for __i__ in range(0, workers))
        }
    }


def check_erc_address_validity(w3_gateway, erc_address):
    """check validity"""
    erc_address_valid = w3_gateway.isAddress(erc_address)
    if not erc_address_valid:
        logging.critical("Invalid user address")
    erc_address = w3_gateway.toChecksumAddress(erc_address)
    logging.debug("User address %s is valid : %s", erc_address, erc_address_valid)
    return erc_address, erc_address_valid


def reset_transaction():
    return {
        "signed_transaction": None,
        "nonce": None,
    }


def reset_signed_transaction():
    return {"signed_transaction": None}


def signed_transaction(transaction, read_web3):
    return read_web3.sign_transaction(transaction[0], transaction[1])


async def send_raw_transaction(signed_transaction, write_web3):
    return await write_web3.send_raw_transaction(signed_transaction.rawTransaction)


async def nonce(worker_address, read_web3):
    return await read_web3.eth.get_transaction_count(worker_address)


async def spot_data(cid, DataSpotting):
    # todo: "1" is for twitter.com, it should be specified dynamicaly
    try:
        return DataSpotting.functions.SpotData([cid], ["1"], [100], "")
    except Exception:
        logging.error("Error calling SpotData")


async def build_transaction(transaction, worker_address, nonce, default_gas_price):
    try:
        return await transaction.build_transaction(
            {"nonce": nonce, "from": worker_address, "gasPrice": default_gas_price}
        )
    except Exception:
        logging.error("Error building transaction")
