#! python3.10
'''
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S

          Supported composition for EXD mining.
'''
import aiohttp
import asyncio
import os
import json
import yaml
import random

from exorde.bindings import wire

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

def choose_w3_gateway(w3_instances):
    random.choice(w3_instances)

async def instanciate_w3():
    def load_yaml(path):
        with open(path, 'r') as _file:
            yaml_data = yaml.safe_load(_file)
            return yaml_data

    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.json(content_type=None)

    # retrieve configuration
    current_directory = os.path.dirname(os.path.abspath(__file__))
    network = load_yaml(f'{current_directory}/network.yaml')
    protocol = load_yaml(f'{current_directory}/protocol.yaml')
    async with aiohttp.ClientSession() as session:
        requests = []
        for __name__, path in protocol['ABI'].items():
            url = f"{protocol['source']}{path}"
            request = asyncio.create_task(fetch(session, url))
            requests.append(request)
        abis = await asyncio.gather(*requests)
        contracts = await fetch(
            session,
            f"{protocol['source']}/{protocol['contracts']}"
        )

    # instanciate web3 instances
    w3_instances = []
    for _urlSkale in network[protocol['target']]['_urlSkale']:
        w3_instance = Web3(Web3.HTTPProvider(_urlSkale))
        w3_instance.middleware_onion.add(cache_middleware)
        w3_instances.append({
            'w3': w3_instance,
        })

    return {
        'network': network,
        'protocol': protocol,
        'w3_instances': w3_instances,
        'abi': { abi['contractName']: abi for abi in abis }
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

def twitter_to_exorde_format(data: dict) -> dict:
    return {
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
