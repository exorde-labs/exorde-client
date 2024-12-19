
from time import sleep
import sys
import requests
from web3 import Web3
from web3.middleware import simple_cache_middleware
from random import randint
import logging

from quality_report import create_report

MAX_RETRIES = 3
address_reader_abi_url = 'https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/AddressReader.json'
network_config_url = 'https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ClientNetworkConfig.json'
netConfig_testnet = requests.get(network_config_url, timeout=5).json()

AddressMasterReader_addr = "0xf095c5aDcc6720BA43AEe1041bD3D69E3eaf0720"

# select one of _urlSkale2, _urlSkale1, _urlSkale3 randomly
random_int = randint(1, 3)
network_name_id = { "testnet":"testnet-B", "mainnet":"testnet-A" }
selected_syncnode_key = f"_urlSkale{random_int}"
RPC_endpoint = netConfig_testnet["testnet-A"][0][selected_syncnode_key]
w3_reader = Web3(Web3.HTTPProvider(RPC_endpoint))
AddressMasterReader_abi_json =  requests.get(address_reader_abi_url, timeout=5).json()
AddressMasterReader = w3_reader.eth.contract(AddressMasterReader_addr, abi=AddressMasterReader_abi_json)
is_mainnet_selected = True

def get_contracts_abis_from_git():
	to = 10
	abis = dict()
	abis["EXDT"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/EXDT/EXDT.json", timeout=to).json()
	abis["DataSpotting"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/DataSpotting.sol/DataSpotting.json", timeout=to).json()
	abis["StakingManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/StakingManager.sol/StakingManager.json", timeout=to).json()
	abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
	abis["AddressManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/AddressManager.sol/AddressManager.json", timeout=to).json()
	abis["Parameters"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/Parameters.sol/Parameters.json", timeout=to).json()

	return abis

# Function to load JSON data from a URL
def load_json_from_url(url):
    response = requests.get(url)
    data = response.json()
    return data



base_abis = get_contracts_abis_from_git()

# this function assumes is_mainnet_select equal to NOT is_testnet_selected
def get_addresses_contracts(is_mainnet_selected):
    # URL of ContractsAddresses.json
    contracts_addresses_url = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ContractsAddresses.json"

    # Load ContractsAddresses.json
    contracts_addresses_data = load_json_from_url(contracts_addresses_url)

    selected_addresses = None
    # Convert the data to dictionaries
    if is_mainnet_selected:
        selected_addresses = contracts_addresses_data[network_name_id["mainnet"]]
    else:
        selected_addresses = contracts_addresses_data[network_name_id["testnet"]]

    return selected_addresses


contracts_addresses = get_addresses_contracts(is_mainnet_selected)
dataspotting_addr = contracts_addresses['DataSpotting']

social_media_domains = [
    "4chan",
    "4channel.org",
    "reddit.com",
    "twitter.com",
    "bsky.app",
    "bluesky.com",
    "bluesky.app",
    "t.com",
    "x.com",
    "youtube.com",
    "yt.co",
    "lemmy.world",
    "mastodon.social",
    "mastodon",
    "weibo.com",
    "nostr.social",
    "nostr.com",
    "jeuxvideo.com",
    "forocoches.com",
    "bitcointalk.org",
    "ycombinator.com",
    "news.ycombinator.com",
    "tradingview.com",
    "followin.in",
    "seekingalpha.io"
]


####################################################################################################
def extract_sync_nodes(data):
    return data.get("urlSkale", None)

def select_object_by_network_id(json_data, network_id):
    data = json_data
    for obj in data:
        if obj.get("_networkId") == network_id:
            return obj
    return None

# this function assumes is_mainnet_select equal to NOT is_testnet_selected
def get_network_info(is_mainnet_selected):
    # URL of NetworkConfig.json
    network_config_url = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ClientNetworkConfig.json"

    # Load NetworkConfig.json
    network_config_data = load_json_from_url(network_config_url)['testnet-A']

    chain_endpoint = None
    selected_network_config = None
    if is_mainnet_selected:
        selected_network_config = select_object_by_network_id(network_config_data,network_name_id["mainnet"])
    else:
        selected_network_config = select_object_by_network_id(network_config_data,network_name_id["testnet"])

    assert(selected_network_config is not None)

    chain_endpoint = selected_network_config["_urlSkale3"]
    chainID = selected_network_config["_chainID"] 
    webSocket = selected_network_config["_webSocket"] 
    syncNodes = extract_sync_nodes(selected_network_config)

    assert(chain_endpoint is not None)
    assert(chainID is not None)
    assert(webSocket is not None)
    return {"chain_endpoint":chain_endpoint, "chainID":chainID, "webSocket":webSocket, "syncNodes": syncNodes}

def get_last_batch_id(data_contract):    
    LastDataBatchId = None
    for k in range(0, MAX_RETRIES):
        try:                       
            LastDataBatchId = data_contract.functions.getLastCheckedBatchId().call()
        except KeyboardInterrupt:
            print("Stop me!")
            sys.exit(0)
        except Exception as e :
            logging.exception(f"Error: getLastCheckedBatchId(index): {e}")
            sleep(int(2*k+1)) # exponential backoff
            continue
        break
    return LastDataBatchId

def get_batch_files(data_contract, last_batch_id, threshold=10):
    LastDataBatchId = []
    for k in range(0, MAX_RETRIES):
        try:                       
            LastDataBatchId = data_contract.functions.getBatchsFilesByID(
                last_batch_id - threshold, last_batch_id
            ).call()
        except KeyboardInterrupt:
            print("Stop me!")
            sys.exit(0)
        except Exception as e :
            logging.exception(f"Error: getLastCheckedBatchId(index): {e}")
            sleep(int(2*k+1)) # exponential backoff
            continue
        break
    return LastDataBatchId

BATCH_FILES_THRESHOLD = 10

from quality_process_manager import ProcessManager

async def main():
    async with ProcessManager("quality_adapters") as manager:
        network_info = get_network_info(is_mainnet_selected)
        chain_endpoint = network_info["chain_endpoint"]
        w3 = Web3(Web3.HTTPProvider(chain_endpoint))
        data_contract = w3.eth.contract(
            dataspotting_addr, abi=base_abis['DataSpotting']["abi"]
        )
        last_batch_id = get_last_batch_id(data_contract)
        batch_files = get_batch_files(data_contract, last_batch_id)
        selected_batchs = batch_files[:BATCH_FILES_THRESHOLD]
        assert len(selected_batchs), "No batch file was infered"
        await create_report(manager, selected_batchs)

import asyncio

try:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stop me!")
    sys.exit(0)
