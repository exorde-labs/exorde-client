# -*- coding: utf-8 -*-
"""
Dec 15/12/2022 16h43

@author: florent, mathias
Exorde Labs
Version = v1.3.5b
"""

import boto3
from collections import Counter, deque
import csv
import datetime as dt
from datetime import timezone
from dateutil.parser import parse
from eth_account import Account
import facebook_scraper  as fb
from functools import partial
from ftlangdetect import detect
detect.eprint = lambda x: None
from geopy.geocoders import Nominatim
import html
# from idlelib.tooltip import Hovertip
from iso639 import languages
import itertools
import json
# import keyboard
# import libcloud
from lxml.html.clean import Cleaner
import numpy as np
from operator import itemgetter
import os
import pandas as pd
from pathlib import Path
import pickle
# from PIL import Image, ImageTk, ImageFile
# from plyer import notification
import pytz
from queue import Queue
import random
from random import randint
import re
import requests
from requests_html import HTML
from requests_html import HTMLSession
from scipy.special import softmax, expit
# import shutils
import snscrape.modules
import string
import sys
import threading
import time
import tldextract
# import transformers
# from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, TFAutoModelForSequenceClassification
import unicodedata
import urllib.request
import warnings
import web3
from web3 import Web3, HTTPProvider
import webbrowser
import yake
import warnings
warnings.filterwarnings("ignore")
import hashlib
# try:
#     import logging, timeit
#     logging.basicConfig(level=logging.DEBUG, format="%(message)s")
# except Exception as e:
#     print(e)

import argparse


RAM_HOLDER_AMOUNT_base = 512000000 # reserve 512Mb of Memory
ramholder = bytearray(RAM_HOLDER_AMOUNT_base)

def DownloadSingleIPFSFile(ipfsHash, timeout_=5, max_trials_=2):
    ## constants & parameters
    _headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.146 Safari/537.36"
        )
    }
    for _ in range(max_trials_):
        try:
            gateways =  requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/ipfs_gateways.txt").text.split("\n")[:-1]
        except:
            time.sleep(3)
    nb_gateways = len(gateways)
    content = None
    ## download each file after the other
    print("\nFetching IPFS file = ",ipfsHash)    
    isOk = False
    # retry all gateways twice, after pause of 10s in between, before giving up on a batch
    for trial in range(max_trials_):    
        _used_timeout = timeout_ * (1+trial)
        print("trial n°", trial, "/", max_trials_-1)
        ## initialize the gateway loop
        gateway_cursor = 0 
        ### iterate a trial of the download over all gateways we have
        for _ in gateways:
            _used_gateway = gateways[gateway_cursor]
            try:
                _endpoint_url = _used_gateway+ipfsHash
                print("\tDownload via: ",_endpoint_url)
                content = requests.get(_endpoint_url, headers=_headers, stream=False,
                                       timeout=_used_timeout)
                try:
                    content = content.json()                    
                except:
                    print("\t\t--failed to open the content with json")
                    content = None   
                if content is not None:
                    isOk = True
                break
            except Exception as e:
                gateway_cursor += 1
                if gateway_cursor >= nb_gateways:
                    print("\t----Tried all gateways")
                    break     
            ## Break from gateway loop if we got the file
            if isOk:
                break        
            time.sleep(0.5)
        ## Break from trial loop if we got the file
        if isOk:
            break
        time.sleep(0.3)
    return content


def SafeURLDownload(URL, timeout_=2, max_trials_=3):
    ## constants & parameters
    _headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.146 Safari/537.36"
        )
    }
    content = None
    ## download each file after the other
    isOk = False
    # retry all gateways twice, after pause of 10s in between, before giving up on a batch
    for trial in range(max_trials_):  
        _used_timeout = timeout_ * (1+trial)
        # print("trial n°",trial,"/",(max_trials_-1))
        ## initialize the gateway loop
        gateway_cursor = 0 
        ### iterate a trial of the download over all gateways we have
        try:
            _endpoint_url = URL
            if general_printing_enabled:
                print("\tDownloading...  ", _endpoint_url)
            content = requests.get(_endpoint_url, headers=_headers, stream=False,
                                   timeout=_used_timeout)
            if content is not None:
                isOk = True
            break
        except Exception as e:
            if general_printing_enabled:
                print("Fail: ",e)
        ## Break from trial loop if we got the file
        if isOk:
            break
        time.sleep(0.3)
    return content

def SelfUpdateProcedure():
    launcher_fp = 'Launcher.py' 
    try:
        req = requests.get("https://raw.githubusercontent.com/exorde-labs/ExordeModuleCLI/main/Launcher.py")
        launcher_code_content = req.content
        github_launcher_code_text = req.text
        if len(github_launcher_code_text) < 100:
            raise ValueError('Error fetching a valid Launcher code.') 
        github_launcher_sig = str(hashlib.md5(launcher_code_content).hexdigest())
        # Open,close, read file and calculate MD5 on its contents 
        with open(launcher_fp, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()    
            # pipe contents of the file through
            local_launcher_sig = str(hashlib.md5(data).hexdigest())
        print("Local version signature = ",local_launcher_sig, " Latest (github) version signature = ",github_launcher_sig)
    except Exception as e:
        print("Init error: ",e)

    try:    
        if(local_launcher_sig != github_launcher_sig):
            # overwrite Launcher
            with open(launcher_fp, 'w+', newline='', encoding='utf-8') as filetowrite:
                filetowrite.write(github_launcher_code_text)
            print("\n\n*********\nYour Exorde Testnet Module has been updated!\n ---> Please RESTART the program.\nExorde Labs, 2022\n*********")
            exit(1)
    except Exception as e:
        print("Error :",e)
        print("\n\n***************************\nA new Version has been released, you need to download the new version (CLI or Docker).\
        \nPlease download the latest code at https://github.com/exorde-labs/ExordeModuleCLI\nStart from a fresh module installation. Thank you.\nExorde Labs, 2022\n***************************")
        exit(1)

################## ARG PARSING
parser = argparse.ArgumentParser()

parser.add_argument('-m', '--main-address', help='Main Ethereum Address, which will get all REP & EXDT for this local worker contribution. Exorde Reputation is non-transferable. Correct usage example: -m 0x0F67059ea5c125104E46B46769184dB6DC405C42', required=True)
parser.add_argument('-l', '--logging',  help='level of logging in the console: 0 = no logs, 1 = general logs, 2 = validation logs, 3 = validation + scraping logs, 4 = detailed validation + scraping logs (e.g. for troubleshooting)', default = 1)
parser.add_argument('-d', '--debug', nargs='?', help='debug logs', default = 0)
parser.add_argument('-n', '--noloc', nargs='?', help='disable sharing your country info (ONLY) (example: FR, UK, US, SP, etc) for statistics purposes. No personal information is ever sent.', default = 0)

localization_enabled = True
try:            
    args = parser.parse_args()
    argsdict = vars(args)
    main_wallet_ = argsdict['main_address']

    is_main_wallet_valid = Web3.isAddress(main_wallet_)
    if not is_main_wallet_valid:
        print(
            "[Error] INVALID Main-address argument. A valid Ethereum address looks like "
            "'0x0F67059ea5c125104E46B46769184dB6DC405C42'"
        )
        sys.exit(1)
    main_wallet_ = Web3.toChecksumAddress(main_wallet_)

    verbosity_ = int(argsdict['logging'])
    if verbosity_ > 0:
        
        if verbosity_ >= 3:
            verbosity_ = 3
        print(
            "Selected logging Level: ",
            verbosity_,
            (
                ".  (0 = no logs, 1 = general logs, 2 = validation logs, "
                "3 = validation + scraping logs, 4 = detailed validation + scraping logs"
            ),
        )

    debug_ = int(argsdict['debug'])
    if debug_ > 0:
        print("******* [DEBUG LOGS ACTIVATED] *******")

    noloc_ = int(argsdict['noloc'])
    if noloc_ == 1:
        print("[Localization (Country) statistic disabled]")
        localization_enabled = False
except:
    parser.print_help()
    sys.exit(1)

# 0 = all disabled
general_printing_enabled = False
scrape_printing_enabled = False
validation_printing_enabled = False
detailed_validation_printing_enabled = False

sys.stderr = open(os.devnull, "w")  # silence stderr

# 1 = general logs only
if verbosity_ == 1:
    general_printing_enabled = True
# 2 = validation logs
if verbosity_ == 2:
    general_printing_enabled = True
    validation_printing_enabled = True
# 3 = validation + scraping logs
if verbosity_ == 3:
    general_printing_enabled = True
    validation_printing_enabled = True
    scrape_printing_enabled = True
# debug log
if debug_ == 1:
    general_printing_enabled = True
    validation_printing_enabled = True
    scrape_printing_enabled = True
    detailed_validation_printing_enabled = True

################## NETWORK CONNECTION
netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()


random_number = random.randint(1, 100 - 1)
if random_number > 65:
    selected_provider_ = netConfig["_urlSkale"]
else:
    selected_provider_ = netConfig["_urlSkale2"]


w3 = Web3(Web3.HTTPProvider(selected_provider_))
w3Tx = Web3(Web3.HTTPProvider(netConfig["_urlTxSkale"]))


ConfigBypassURL = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/CodeModules.txt"

################## BLOCKCHAIN INTERFACING
to = 60    
contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()
abis = dict()
abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()

contract = w3.eth.contract(contracts["ConfigRegistry"], abi=abis["ConfigRegistry"]["abi"])

config_reg_contract = contract
override_code_dict = dict()
# override_code_dict["_moduleHashContracts_cli"] = "https://bafybeibuxrjwffjeymrjlkd2r35r5rdlzxuavoeympqgr7xrxor6hp3bh4.ipfs.w3s.link/Transaction.py"              # Transaction.py
# override_code_dict["_moduleHashSpotting_cli"] = "https://bafybeifqnq76utn767m4qbwd4j2jg6k3ypwcr2do7gkk3b26ooxfmzgc5e.ipfs.w3s.link/Scraper.py"                   # Scraper.py
# override_code_dict["_moduleHashSpotChecking_cli"] = "https://bafybeibbygfm276hjion7ocaoyp3wlfodszhlba6jy3b3fzd37zawkfbgi.ipfs.w3s.link/Validator.py"             # Validator.py
# override_code_dict["_moduleHashApp_cli"] = "https://bafybeicdgmxvetbi4yqjztzzroevcfvnwobk6zomsz5nh4lvb3dftyimxa.ipfs.w3s.link/App.py"                            # App.py

########### AUTO UPDATE PROCEDURE ##################
SelfUpdateProcedure()
####################################################

if general_printing_enabled:
    print("\n[INITIAL MODULE SETUP] Downloading code modules on decentralized storage...")

################## READING ONCHAIN CONFIG TO DOWNLOAD LATEST CODE
module_hash_list = ["_moduleHashContracts_cli", "_moduleHashSpotting_cli", "_moduleHashSpotChecking_cli",
                    "_moduleHashApp_cli"]

##############################
bypass_enabled = True
##############################


boot_sleep_delay = randint(5,1*60) # sleep randomly between 30s & 10 minutes
print("[ Network Load Balancing ] Waiting ",boot_sleep_delay, " seconds - System status = Booting.")
time.sleep(boot_sleep_delay)

nb_modules_fetched_from_config = 0
nb_module_to_fetch = len(module_hash_list)

code_array = []

if bypass_enabled == False:
    for im, value in enumerate(module_hash_list):
        #print(value)
        success = False
        trials = 0
        if general_printing_enabled:
            print("\tCode Sub-Module ",(im+1)," / ", len(module_hash_list), end='')
            
        print(" .")
        while(trials < 3):
            print(".",end='')
            try:
                if value  in override_code_dict:
                    URL = override_code_dict[value]
                    code = SafeURLDownload(URL).text
                else:
                    URL = hashValue = contract.functions.get(value).call()
                    code = SafeURLDownload(URL).text
                code_array.append(code)
                success = True
                nb_modules_fetched_from_config += 1
                break
            except:
                time.sleep(2*(trials + 1))
                trials += 1
                
        # if success:
        #     exec(code)

if bypass_enabled or (nb_modules_fetched_from_config != nb_module_to_fetch):
    print("\n****************\n[BYPASS] Fetching from ExordeLabs github: ", ConfigBypassURL)
    bypassModules = requests.get(ConfigBypassURL).json()
    for im, ModuleURL in enumerate(bypassModules):
        #print(value)
        success = False
        trials = 0
        if general_printing_enabled:
            print("\t[Github Override] Code Sub-Module ",(im+1))
        while(trials < 3):
            try:
                code = SafeURLDownload(bypassModules[ModuleURL]).text
                success = True
                break
            except:
                time.sleep(2*(trials + 1))
                trials += 1
                
        if(success == True):
            exec(code)
else: # run the modules from the config
    time.sleep(1)
    for code_ in code_array:
        exec(code_)
        time.sleep(1)



############# LAUNCH THE CORE MODULE
desktop_app()

with open("localConfig.json", "r") as f:
    localconfig = json.load(f)
            
while True:
    # sleep to maintain alive
    time.sleep(5*60)
    SelfUpdateProcedure()
    ## check update   
    try:
        if general_printing_enabled:
            print("[UPDATE SYSTEM] Checking new updates...")    
        try:
            _version = config_reg_contract.functions.get("version").call()
            _lastInfo = config_reg_contract.functions.get("lastInfo").call()
        except:
            _version = localconfig["ExordeApp"]["lastUpdate"]
        
        if("lastUpdate" not in localconfig["ExordeApp"]):            
            localconfig["ExordeApp"]["lastUpdate"] = _version
            with open("localConfig.json", "w") as f:
                json.dump(localconfig, f)
        try:
            print("[UPDATE SYSTEM] Last Version: ", localconfig["ExordeApp"]["lastUpdate"], "New:", _version)
        except:
            print("[UPDATE SYSTEM] No Last Version: ", "New:", _version)
            
        if localconfig["ExordeApp"]["lastUpdate"] != _version:
            print("\n\n\n***************************\n",\
                "Version {}".format(_version)," has been released.\nPlease restart your module to continue.\nAuto quit, please relaunch the program. \n")
            print("Last message from Exorde Labs => ",_lastInfo,"\n***************************.")
            # update localconfig, important
            localconfig["ExordeApp"]["lastUpdate"] = _version
            with open("localConfig.json", "w") as f:
                json.dump(localconfig, f)
            exit(1)
    except Exception as e:
        print(e)
