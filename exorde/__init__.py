#! python3.10
'''
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S
  
  Supported interface implementation for EXD mining.

'''
import logging
import aiohttp
import asyncio
import os
import random
import yaml
from typing import Union
import string
import json

from aiosow.command import run
from aiosow.bindings import read_only 

from eth_account import Account
from web3 import Web3
from web3.middleware.cache import _simple_cache_middleware as cache_middleware

def load_yaml(path):
    with open(path, 'r') as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data

async def fetch(session, url) -> Union[tuple, dict]:
    async with session.get(url) as response:
        return await response.json(content_type=None)

configuration = lambda: {
    'configuration': load_yaml(
        os.path.dirname(os.path.abspath(__file__)) + '/configuration.yaml'
    )
}

# cnf stands for configuration
# Data-coupling because contract instanciation requires Contract & ABIS 
async def contracts_and_abi_cnf(configuration):
    async with aiohttp.ClientSession() as session:
        requests = []
        for __name__, path in configuration['ABI'].items():
            url = f"{configuration['source']}{path}"
            request = asyncio.create_task(fetch(session, url))
            requests.append(request)
        abis = await asyncio.gather(*requests)
        contracts = dict(await fetch( # casted to dict for the IDEs
            session,
            f"{configuration['source']}/{configuration['contracts']}"
        ))
    logging.info(
        'abis loaded are : %s', ', '.join([abi['contractName'] for abi in abis])
    )
    return {
        'contracts_cnf': read_only(contracts),
        'abi_cnf': read_only({ abi['contractName']: abi for abi in abis })
    }

def instanciate_w3(url):
    w3_instance = Web3(Web3.HTTPProvider(url))
    w3_instance.middleware_onion.add(cache_middleware)
    return w3_instance

write_web3 = lambda configuration: {
    'write_web3': instanciate_w3(
        configuration[configuration['target']]['_urlTxSkale']
    )
}

read_web3 = lambda configuration: {
    'read_web3': instanciate_w3(
        random.choice(
            configuration[configuration['target']]['_urlSkale']
        )
    )
}

def contract(name, read_w3, abi_cnf, contracts_cnf, configuration):
    try:
        return read_w3.eth.contract(
            contracts_cnf()[configuration['target']][name],
            abi=abi_cnf()[name]["abi"]
        )
    except:
        logging.debug('Skipped contract instanciation for %s', name)
        return None

contracts = lambda read_w3, abi_cnf, contracts_cnf, configuration: {
    name: contract(name, read_w3, abi_cnf, contracts_cnf, configuration) 
    for name in contracts_cnf()[configuration['target']]
}

def worker_address():
    '''Generates an ERC address and key'''
    random.seed(random.random())
    base_seed = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=256)
    )
    acct = Account.create(base_seed)
    logging.debug('Generated a key "%s"', acct.address)
    return acct

def check_erc_address_validity(w3_gateway, erc_address):
    '''check validity'''
    erc_address_valid = w3_gateway.isAddress(erc_address)
    if not erc_address_valid:
        logging.critical("Invalid user address")
    erc_address = w3_gateway.toChecksumAddress(erc_address)
    logging.debug(
        'User address %s is valid : %s',
        erc_address,
        erc_address_valid
    )
    return erc_address, erc_address_valid

worker_addresses = lambda workers: {
    'worker_addresses': {
        addr: key for addr, key in 
            (worker_address() for __i__ in range(0, workers))
    }
}
reset_transactions = lambda: {
    'signed_transaction': None,
    'transactions': [],
    'nounce': None
}
select_transaction_to_send = lambda transactions: {
    'signed_transaction': transactions[0],
    'transactions': transactions[1:]
}
signed_transaction = lambda transaction, read_web3: read_web3.sign_transaction(
    transaction[0], transaction[1]
)
send_transaction = lambda transaction, transactions: {
    'transactions': transactions + [transaction]
}
send_raw_transaction = lambda signed_transaction, write_web3: write_web3.send_raw_transaction(
    signed_transaction.rawTransaction
)
nounce = lambda worker_address, read_web3: read_web3.eth.get_transaction_count(
    worker_address
)
twitter_to_exorde_format = lambda data: {
    "Author": "",
    "Content": data['full_text'],
    "Controversial": data.get('possibly_sensitive', False),
    "CreationDateTime": data['created_at'],
    "Description": "",
    "DomainName": "twitter.com",
    "Language": data['lang'],
    "Reference": "",
    "Title": "",
    "Url": f"https://twitter.com/a/status/{data['id_str']}",
    "internal_id": data['id'],
    "media_type": "",
    # "source": data['source'], # new
    # "nbQuotes": data['quote_count'], # new
    "nbComments": data['reply_count'],
    "nbLikes": data['favorite_count'],
    "nbShared": data['retweet_count'],
    # "isQuote": data['is_quote_status'] # new
}

spot_block = lambda entities: {
    "entities": entities
}

async def upload_to_ipfs(value, ipfs_path):
    async with aiohttp.ClientSession() as session:
        async with session.post(ipfs_path, data=json.dumps(value), headers={
            'Content-Type': 'application/json'
        }) as resp:
            if resp.status == 200:
                response = await resp.json()
                return response
            else:
                content = await resp.text()
                raise Exception(f'Failed to upload to IPFS ({resp.status}) -> {content}')

launch = lambda:run('exorde')
