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
import json
import yaml

from exorde.bindings import wire
from exorde.utils import read_only 

from web3 import Web3
from web3.middleware.cache import _simple_cache_middleware as cache_middleware

PARAMETERS = {
    'ethereum_address': {
        'help': 'Main Ethereum Address to be rewarded',
        'default' :None
    },
    'ipfs_path': {
        'default': 'http://ipfs-api.exorde.network/add',
    }
}

def load_yaml(path):
    with open(path, 'r') as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data

async def fetch(session, url):
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
        contracts = await fetch(
            session,
            f"{configuration['source']}/{configuration['contracts']}"
        )
    logging.info('abis loaded are : %s', ', '.join([abi['contractName'] for abi in abis]))
    return {
        'contracts_cnf': read_only(**contracts),
        'abi_cnf': read_only(**{ abi['contractName']: abi for abi in abis })
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

contract = lambda name, read_w3, abi_cnf, contracts_cnf, configuration: read_w3.eth.contract(
    contracts_cnf()[configuration['target']][name],
    abi=abi_cnf()[name]["abi"]
)

contracts = lambda read_w3, abi_cnf, contracts_cnf, configuration: {
    name: contract(name, read_w3, abi_cnf, contracts_cnf, configuration) 
    for name in contracts_cnf()[configuration['target']]
}

reset_transactions = lambda: {
    'transactions': [],
    'nounce': None 
}

def register_main_erc_address():
    '''Transaction which binds an ethereum address to workers'''
    # am = self.cm.instantiateContract("AddressManager")
    # increment_tx = am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
    #     {
    #        'from': self.localconfig["ExordeApp"]["ERCAddress"],
    #        'gasPrice': w3.eth.gas_price,
    #        'nonce': w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"]),
    #    }
    # )
    # self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey, True))

def claim_data_batch():
    '''Transaction which registers ownership of an uploaded data-block'''
    # contract = self.app.cm.instantiateContract("DataSpotting")
    # increment_tx = contract.functions.SpotData([res], [domNames], batchSize, 'Hi Bob!').buildTransaction(
    # {
    #     'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
    #     'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
    #     'gasPrice': w3.eth.gas_price,
    #     'gas':200000000
    # })
    # self.app.tm.waitingRoom.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))

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

formated_tweet_trigger, formated_tweet_wire = wire(batch=100)
async def format_tweet(tweet, **kwargs):
    formated = twitter_to_exorde_format(tweet)
    await formated_tweet_trigger(formated, **kwargs)

async def spot(data:list, ipfs_path):
    tweets = [tweet[0] for tweet in data]
    spot_block = {
        "entities": tweets,
        "keyword": "",
        "links": "",
        "medias": "",
        "spotterCountry": "",
        "tokenOfInterest": ""
    }
    print(json.dumps(spot_block, indent=4), ipfs_path)
    # await upload_to_ipfs(data, ipfs_path)
