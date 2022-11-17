# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 14:20:53 2022

@author: flore
"""

# import boto3
# from collections import Counter, deque
# import datetime as dt
# from datetime import timezone
# from eth_account import Account
# import facebook_scraper  as fb
# from geopy.geocoders import Nominatim
# import html
# from idlelib.tooltip import Hovertip
# import itertools
# import json
# from langdetect import detect
# import libcloud
# from lxml.html.clean import Cleaner
# import numpy as np
# import os
# import pandas as pd
# from pathlib import Path
# import pickle
# from PIL import Image, ImageTk, ImageFile
# import pytz
# from queue import Queue
# import random
# import re
# import requests
# from requests_html import HTML
# from requests_html import HTMLSession
# import shutils
# import sklearn
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import PassiveAggressiveClassifier
# from sklearn.metrics import accuracy_score, confusion_matrix
# from sklearn.naive_bayes import MultinomialNB
# import snscrape.modules
# import string
# import threading
# import time
# import tkinter as tk
# from tkinter import ttk
# import tkinter.messagebox
# import tldextract
# import unicodedata
# import warnings
# import web3
# from web3 import Web3, HTTPProvider
# import webbrowser
# import yake


default_gas_amount = 3_000_000

class ContractManager():
    
    def __init__(self, address = "", key =""):
        
        self._AccountAddress = address
        self._AccountKey = key
        self._TransactionManager = TransactionManager(self)
        self.netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
        self.w3 = Web3(Web3.HTTPProvider(self.netConfig["_urlTxSkale"]))

        
        to = 60
        self.contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()
        self.abis = dict()
        #self.abis["AttributeStore"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/AttributeStore.json", timeout=to).json()
        self.abis["EXDT"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/DAOToken.sol/DAOToken.json", timeout=to).json()
        self.abis["DataSpotting"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/DataSpotting.sol/DataSpotting.json", timeout=to).json()
        #self.abis["DataFormatting"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/DataFormatting.sol/DataFormatting.json", timeout=to).json()
        #self.abis["DLL"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/DLL.json", timeout=to).json()
        #self.abis["IEtherBase"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/sfueldistribute.sol/IEtherbase.json", timeout=to).json()
        self.abis["Reputation"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/Reputation.sol/Reputation.json", timeout=to).json()
        #self.abis["IRewardManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/IRewardManager.json", timeout=to).json()
        #self.abis["IStakeManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/IStakeManager.json", timeout=to).json()
        #self.abis["RandomAllocator"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/RandomAllocator.sol/RandomAllocator.json", timeout=to).json()
        self.abis["RewardsManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/RewardsManager.sol/RewardsManager.json", timeout=to).json()
        #self.abis["SFuelContracts"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/sfueldistribute.sol/SFuelContracts.json", timeout=to).json()
        self.abis["StakingManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/StakingManager.sol/StakingManager.json", timeout=to).json()
        self.abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
        self.abis["AddressManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/AddressManager.sol/AddressManager.json", timeout=to).json()
        #self.abis["Parameters"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/Parameters.sol/Parameters.json", timeout=to).json()

    def instantiateContract(self, arg: str):
        
        # to = 60
        # self.contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()
        # self.abis = dict()
        # #self.abis["AttributeStore"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/AttributeStore.json", timeout=to).json()
        # self.abis["EXDT"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/DAOToken.sol/DAOToken.json", timeout=to).json()
        # self.abis["DataSpotting"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/DataSpotting.sol/DataSpotting.json", timeout=to).json()
        # #self.abis["DataFormatting"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/DataFormatting.sol/DataFormatting.json", timeout=to).json()
        # #self.abis["DLL"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/DLL.json", timeout=to).json()
        # #self.abis["IEtherBase"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/sfueldistribute.sol/IEtherbase.json", timeout=to).json()
        # self.abis["Reputation"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/Reputation.sol/Reputation.json", timeout=to).json()
        # #self.abis["IRewardManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/IRewardManager.json", timeout=to).json()
        # #self.abis["IStakeManager"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/DataSpotting.sol/IStakeManager.json", timeout=to).json()
        # #self.abis["RandomAllocator"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/RandomAllocator.sol/RandomAllocator.json", timeout=to).json()
        # self.abis["RewardsManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/RewardsManager.sol/RewardsManager.json", timeout=to).json()
        # #self.abis["SFuelContracts"] = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ABIs/worksystems/sfueldistribute.sol/SFuelContracts.json", timeout=to).json()
        # self.abis["StakingManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/StakingManager.sol/StakingManager.json", timeout=to).json()
        # self.abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
        # self.abis["AddressManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/AddressManager.sol/AddressManager.json", timeout=to).json()
        # #self.abis["Parameters"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/Parameters.sol/Parameters.json", timeout=to).json()

        contract = self.w3.eth.contract(self.contracts[arg], abi=self.abis[arg]["abi"])
        return contract
    
    def readStake(self):
        
        sm = self.instantiateContract("StakingManager")
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        # for i in range(5):
        #     try:
        #         stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        #         break
        #     except Exception as e:
        #         print(e)
        if(stakeAmount > Web3.toWei(25, 'ether')):
            return True
        else:
            return False
        
    def StakeManagement(self, transactManager):
        
        contract = self.instantiateContract("EXDT")
        sm = self.instantiateContract("StakingManager")
        
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        stakeAllocated = sm.functions.AllocatedStakedAmountOf(self._AccountAddress).call()
        # for i in range(5):
        #     try:
        #         stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        #         stakeAllocated = sm.functions.AllocatedStakedAmountOf(self._AccountAddress).call()
        #         break
        #     except Exception as e:
        #         print(e)
        
        if(stakeAmount >= 100 ):
            return True
        else:

            try:
                amount = Web3.toWei(100, 'ether')
                increment_tx = contract.functions.approve(self.contracts["StakingManager"], amount).buildTransaction(
                    {
                        'from': self._AccountAddress,
                        'gasPrice': self.w3.eth.gas_price,
                        'nonce': self.w3.eth.get_transaction_count(self._AccountAddress),
                    }
                )
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
                
                amount_check = contract.functions.allowance(self._AccountAddress, self.contracts["StakingManager"]).call()
                # for i in range(5):
                #     try:
                #         amount_check = contract.functions.allowance(self._AccountAddress, self.contracts["StakingManager"]).call()
                #         break
                #     except Exception as e:
                #         print("stake_management1", e)
                        
                
                increment_tx = sm.functions.deposit(Web3.toWei(100, 'ether')).buildTransaction(
                   {
                       'from': self._AccountAddress,
                       'gasPrice': self.w3.eth.gas_price,
                       'nonce': self.w3.eth.get_transaction_count(self._AccountAddress),
                   }
               )
                
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
               
                increment_tx = sm.functions.Stake(Web3.toWei(100, 'ether')).buildTransaction(
                   {
                       'from': self._AccountAddress,
                       'gasPrice': self.w3.eth.gas_price,
                       'nonce': self.w3.eth.get_transaction_count(self._AccountAddress),
                   }
               )
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
                time.sleep(30)
            except Exception as e:
                pass
                #print("stake_management2", e)
            return True
    
class TransactionManager():
    
    def __init__(self, cm):
        
        self.netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
        self.w3 = Web3(Web3.HTTPProvider(self.netConfig["_urlSkale"]))
        self.waitingRoom = Queue()
        self.waitingRoom_VIP = Queue()
        self.run = True
        self.last_block = self.w3.eth.get_block('latest')["number"]-1
        self.cm = cm
        x = threading.Thread(target=self.SendTransactions)        
        x.daemon = True
        x.start()
        
    def SendTransactions(self):
        
        while True:
            
            # try:
            #     newNetConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
            # except:
            #     newNetConfig = None
            
            # if(newNetConfig != None):
            #     self.netConfig = newNetConfig
            
            if(self.waitingRoom_VIP.qsize() == 0 and self.waitingRoom.qsize() == 0):
                time.sleep(5)
                pass

            else:
                
                try:
                    if(self.waitingRoom_VIP.qsize() != 0):
                        while(self.w3.eth.get_block('latest')["number"] <= self.last_block):
                            pass
                        
                        isSent = False
                        while(isSent == False):
                            try:
                                increment_tx = self.waitingRoom_VIP.get() 
                                
                                old = increment_tx[0]["nonce"]
                                increment_tx[0]["nonce"] = self.w3.eth.get_transaction_count(increment_tx[1])

                                gas = default_gas_amount
                                try:
                                    gasEstimate = self.w3.eth.estimate_gas(increment_tx[0])*1.5
                                    if gasEstimate > 30_000:
                                        gas = gasEstimate
                                except  Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Gas estimation failed: ",e)

                                increment_tx[0]["gas"] = int(round(int(gas),0))

                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)
            
                                tx_create = self.w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])
                                tx_hash = self.w3.eth.send_raw_transaction(tx_create.rawTransaction)
                                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                                # print()
                                # print(tx_receipt)
                                
            
                                self.last_block = self.w3.eth.get_block('latest')["number"]
                                isSent = True
                            except Exception as e:
                                # print("VIP_TX_sending", e)
                                # print()
                                pass
                    
                    else:
                        while(self.w3.eth.get_block('latest')["number"] <= self.last_block):
                            pass
                        
                        isSent = False
                        while(isSent == False):
                            try:
                                increment_tx = self.waitingRoom.get() 
                                
                                old = increment_tx[0]["nonce"]
                                increment_tx[0]["nonce"] = self.w3.eth.get_transaction_count(increment_tx[1])
                                gas = default_gas_amount
                                try:
                                    gasEstimate = self.w3.eth.estimate_gas(increment_tx[0])*1.5
                                    if gasEstimate > 30_000:
                                        gas = gasEstimate
                                except  Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Gas estimation failed: ",e)

                                increment_tx[0]["gas"] = int(round(int(gas),0))
                                
                
                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)

                                tx_create = self.w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])
                                tx_hash = self.w3.eth.send_raw_transaction(tx_create.rawTransaction)                                
                                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                                # print()
                                # print(tx_receipt)
                
                                self.last_block = self.w3.eth.get_block('latest')["number"]
                                isSent = True
                            except Exception as e:
                                # print("TX_sending", e)
                                # print()
                                pass
                except Exception as e:
                    #print("SendTransactions", e)
                    pass
                    
                    
#print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"TRANSACTION", "import", "LOADED"))                    
