import aiohttp, asyncio, logging
from typing import Union
import json

async def get_quality_contracts_and_abi_cnf(
    protocol_configuration, configuration
):
    with open("./exorde/address_manager.json", "r") as json_file:
        address_manager_contract = json.load(json_file)
    with open("./exorde/data_spotting.json", "r") as json_file:
        data_spotting_contract = json.load(json_file)

    return {
        "contracts_cnf": {
            "testnet-A": {
                "abi_cnf": {
                    "address_manager": address_manager_contract,
                    "data_spotting": data_spotting_contract
                }
            }
        }
    }

async def get_spotting_contracts_and_abi_cnf(
    protocol_configuration, configuration
):
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

async def get_contracts_and_abi_cnf(
    protocol_configuration, configuration, command_line_arguments
):
    if command_line_arguments.quality:
        return await get_spotting_contracts_and_abi_cnf(protocol_configuration, configuration)
    else:
        return await get_spotting_contracts_and_abi_cnf(protocol_configuration, configuration)
