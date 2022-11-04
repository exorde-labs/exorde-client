# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 09:04:47 2022

@author: flore
"""

# import boto3
# from collections import Counter, deque
# import csv
# import datetime as dt
# from datetime import timezone
# from dateutil.parser import parse
# from eth_account import Account
# import facebook_scraper  as fb
# from functools import partial
# from ftlangdetect import detect
# from geopy.geocoders import Nominatim
# import html
# from idlelib.tooltip import Hovertip
# from iso639 import languages
# import itertools
# import json
# import keyboard
# import libcloud
# from lxml.html.clean import Cleaner
# import numpy as np
# from operator import itemgetter
# import os
# import pandas as pd
# from pathlib import Path
# import pickle
# from PIL import Image, ImageTk, ImageFile
# from plyer import notification
# import pytz
# from queue import Queue
# import random
# import re
# import requests
# from requests_html import HTML
# from requests_html import HTMLSession
# from scipy.special import softmax, expit
# import shutils
# import snscrape.modules
# import string
# import sys
# import threading
# import time
# import tkinter as tk
# from tkinter import ttk
# import tkinter.messagebox
# import tldextract
# # import transformers
# # from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, TFAutoModelForSequenceClassification
# import unicodedata
# import urllib.request
# import warnings
# import web3
# from web3 import Web3, HTTPProvider
# import webbrowser
# import yake



# import requests
# import web3
# from web3 import Web3, HTTPProvider
# import time
# import tkinter as tk
# from tkinter import ttk
# import tkinter.messagebox

# from Transaction import ContractManager, TransactionManager
# from Scraper import Scraper
# from Validator import Validator
# import requests



class Widget():
    
    def __init__(self):        
        
        try:
            locInfo = requests.get("http://ipinfo.io/json").json()
            self.userCountry = Web3.toHex(text=json.dumps(locInfo)) #["country"]
        except:
            self.userCountry = Web3.toHex(text="Unknown")
        
        netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
        self.w3 = Web3(Web3.HTTPProvider(netConfig["_urlSkale"]))
        
        if general_printing_enabled:
            print("\n[Init] UPDATING CONFIG")
        self.readLocalConfig()

        
        x = threading.Thread(target=self.submarineManagement)
        x.daemon = True
        x.start()


    def monitor(self):
        
        try:
            if(spotThread.is_alive() == False):
                del self.spotThread
                self.spotThread = threading.Thread(target=self.manage_scraping)
                
                self.spotThread.daemon = True
                self.spotThread.start()
            if(self.checkThread.is_alive() == False):
                del self.checkThread
                self.checkThread = threading.Thread(target=self.manage_checking)
                self.spotThread.daemon = True
                self.checkThread.start()
        except:
            pass
        
    def submarineManagement(self):
        
        if general_printing_enabled:
            print("[Init] CREATING UTILS")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "submarineManagement", self.status))
        self.createUtils()

        self.stakeChecking()
        
        if general_printing_enabled:
            print("[Init] CREATING DATA COLLECTION SUBROUTINE")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "submarineManagement", self.status))
        self.sm = Scraper(self)
        self.spotThread = threading.Thread(target=self.sm.manage_scraping)        
        self.spotThread.daemon = True
        self.spotThread.start()
        
        if general_printing_enabled:
            print("[Init] CREATING VALIDATION SUBROUTINE")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "submarineManagement", self.status))
        
        self.val = Validator(self)
        # self.checkThread = threading.Thread(target=self.val.manage_checking)
        # self.checkThread.start()
        
        
    def to_explorer(self):
        
        x = threading.Thread(target=webbrowser.open_new, args=("http://explorer.exorde.network/",))
        x.daemon = True
        x.start()
        #webbrowser.open_new("http://explorer.exorde.network/")
        
    def openFormattingScreen(self):
        
        x = threading.Thread(target=webbrowser.open_new, args=("https://light-vast-diphda.explorer.mainnet.skalenodes.com/address/{}/transactions".format(self.localconfig["ExordeApp"]["ERCAddress"]),))
        x.daemon = True
        x.start()
        #webbrowser.open_new("https://light-vast-diphda.explorer.mainnet.skalenodes.com/address/{}/transactions".format(self.localconfig["ExordeApp"]["ERCAddress"]))

    def Close(self):
        if general_printing_enabled:
            print("Closing...")
        exit(1)
        
    
    def select_random_faucet_pk(self):
        Private_key_base_ = "deaddeaddeaddead5fb92d83ed54c0ea1eb74e72a84ef980d42953caaa6d"
        ## faucets private keys are ["Private_key_base"+("%0.4x" % i)] with i from 0 to 499. Last 2 bytes is the selector.

        selected_faucet_index_ = random.randrange(0,499+1,1)  # [select index between 0 & 499 (500 faucets)]

        hex_selector_bytes = "%0.4x" % selected_faucet_index_
        faucet_private_key_ = Private_key_base_ + hex_selector_bytes  
        return selected_faucet_index_, faucet_private_key_


    def autofund(self):
        if general_printing_enabled:
            print("[Initial Auto Faucet] Top up sFuel & some EXDT to worker address...")
        
        ### DECODE PRIVATE KEY FOR STORAGE
        
        user_address = self.localconfig["ExordeApp"]["ERCAddress"]

        ##### 0 - CHECK VALIDITY                
        is_user_address_valid = self.w3.isAddress(user_address)
        if is_user_address_valid == False:
            print("[Init] INVALID USER ADDRESS, ABORT")
            os._exit(1)
        user_address = self.w3.toChecksumAddress(user_address)
                

        chainId_ = 2139927552
        EXDT_token_address = "0xcBc357F3077989B4636E93a8Ce193E05cd8cc56E"

        faucet_success = False
        while faucet_success == False:
            try:
                # select random faucet out of the  500 ones
                (fi, Private_key) = self.select_random_faucet_pk()
                if general_printing_enabled:
                    print("[Faucet] selecting Auto-Faucet n°",fi)
                faucet_address = self.w3.eth.account.from_key(Private_key).address
                
                               
                ### 1 - SEND FUEL FIRST
                #print("SEND FUEL")
                signed_txn = self.w3.eth.account.sign_transaction(dict(
                    nonce=self.w3.eth.get_transaction_count(faucet_address),
                    gasPrice=self.w3.eth.gas_price,
                    gas=1000000,
                    to=user_address,
                    value=500000000000000,
                    data=b'Hi Exorde!',
                    #type=2,   (optional) the type is now implicitly set based on appropriate transaction params
                    chainId=chainId_,
                ),
                Private_key,
                )
                
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                #print(f'Tx successful with hash: { tx_receipt.transactionHash.hex() }')
                    
                
                ### 1 - SEND EXDT TOKENS                    
                token_abi = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/DAOToken.sol/DAOToken.json").json()["abi"]
                
                tok_contract = self.w3.eth.contract(EXDT_token_address, abi=token_abi)
                
                token_amount_to_send = 200000000000000000000 # 200 tokens EXDT
                increment_tx = tok_contract.functions.transfer(user_address, token_amount_to_send).buildTransaction({
                        'from': faucet_address,
                        'nonce': self.w3.eth.get_transaction_count(faucet_address),
                        'value': 0,
                        'gas': 1000000,
                        'gasPrice': self.w3.eth.gas_price,
                })
                
                tx_create = self.w3.eth.account.sign_transaction(increment_tx, Private_key)
                tx_hash = self.w3.eth.send_raw_transaction(tx_create.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

                time.sleep(1)
                _trials = 3
                read_status = False
                for i in range(_trials):
                    try:                              
                        token_balance = tok_contract.functions.balanceOf(user_address).call()
                        user_token_balance = w3.fromWei(token_balance, 'ether')
                        user_sfuel_balance = w3.eth.get_balance(user_address)
                        read_status = True
                    except:
                        time.sleep((1+int(i)))
                
                if read_status == False:
                    continue

                print('[Faucet] Worker EXDT Balance:', user_token_balance, " ")
                print('[Faucet] Worker sFuel Balance:', user_sfuel_balance, " sFUEL")

                if user_token_balance >= 100 and user_sfuel_balance > 0:
                    faucet_success = True
                    print("[Faucet] Auto-Faucet n°",fi, " Success.")
                break
            except:
                print("[Faucet] Auto-Faucet n°",fi, " Failure... retrying.")
                time.sleep(2)
                continue

        
    def createUtils(self):
        
        self.cm = ContractManager(self.localconfig["ExordeApp"]["ERCAddress"], self.pKey)
        self.tm = TransactionManager(self.cm)
        


            
    def generateLocalKey(self):
        random.seed(random.random())
        baseSeed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=256))
        acct = Account.create(baseSeed)
        key = acct.key
        return acct.address, key
    
    def stakeChecking(self):
        
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "stakeChecking", self.status))
        
        if(self.cm.readStake() == True):

            self.am = self.cm.instantiateContract("AddressManager")

            if(self.localconfig["ExordeApp"]["MainERCAddress"] != ""):

                increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                    {
                        'from': self.localconfig["ExordeApp"]["ERCAddress"],
                        'gasPrice': self.w3.eth.gas_price,
                        'nonce': self.w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"]),
                    }
                )
                self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))
        else:
            
            
            # https://api.faucet.exorde.network/fundAccount/{{account}}
            
            requests.post("https://api.faucet.exorde.network/fundAccount/"+self.localconfig["ExordeApp"]["ERCAddress"])
            
            self.am = self.cm.instantiateContract("AddressManager")

            if(self.localconfig["ExordeApp"]["MainERCAddress"] != ""):

                increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                    {
                        'from': self.localconfig["ExordeApp"]["ERCAddress"],
                        'gasPrice': self.w3.eth.gas_price,
                        'nonce': self.w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"]),
                    }
                )
                self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))

        self.cm.StakeManagement(self.tm)    
        if general_printing_enabled:
            print("[Init] Staking requirement OK")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "stakeChecking", self.status))
        


    def readLocalConfig(self):
        self.configFile = "localConfig.json"
        
        if general_printing_enabled:
            print("[Init] READING CONFIG FILE")
    
        with open("localConfig.json", "r") as f:
            self.localconfig = json.load(f)
        
        print("[Init] Current Config : ",self.localconfig)
        new_conf = self.localconfig
        if new_conf is None:
            new_conf = dict()
            
        new_conf["ExordeApp"]["MainERCAddress"] = str(main_wallet_)
        
        if("Updated" not in self.localconfig["ExordeApp"] or self.localconfig["ExordeApp"]["Updated"] == 0):
            
            if general_printing_enabled:
                print("[Init] FIRST WORKER LAUNCH")
                
            new_conf["ExordeApp"]["ERCAddress"], self.pKey = self.generateLocalKey()
            new_conf["ExordeApp"]["Updated"] = 1
            new_conf["ExordeApp"]["SendCountryInfo"] = 1
        
            if general_printing_enabled:
                print("[Init] New Worker Local Address = ",new_conf["ExordeApp"]["ERCAddress"])
                # print("[Init] New Configuration = ",new_conf)
                print("[Init] First funding of the worker wallet")
                self.autofund()
            
            with open('bob.txt', "wb") as file:
                file.write(self.pKey)
                
            self.localconfig = new_conf    
            
        else:
            with open('bob.txt', "rb") as file:
                self.pKey = file.read()
        
        # updating localconfig with new MainERCAddress
        with open("localConfig.json", "w") as f:
            json.dump(new_conf,f)
                
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"WIDGET", "__init__", self.status))
        
        try:
            self.allowGeoCoordSending = self.localconfig["ExordeApp"]["SendCountryInfo"]
        except:
            self.allowGeoCoordSending = 1
                 


    
    # def createLocalConfig(self):
    #     if general_printing_enabled:
    #         print("[Init] CREATING CONFIG FILE")
    #     if(self.localconfig["ExordeApp"]["MainERCAddress"] == ""):
    #         self.localconfig["ExordeApp"]["MainERCAddress"] = str(main_wallet_)

    #         self.autofund()
    #         with open("localConfig.json", "w") as f:
    #             json.dump(self.localconfig,f)
    

    def updateLocalConfig(self):
        
        with open("localConfig.json", "w") as f:
            json.dump(self.localconfig,f)
            
    def changeAllowanceGeo(self):
        
        
        if(self.allowGeoCoordSending == 1):
            self.allowGeoCoordSending = 0
        else:
            self.allowGeoCoordSending = 1
            
        self.localconfig["ExordeApp"]["SendCountryInfo"] = self.allowGeoCoordSending
        self.updateLocalConfig()

        
# class UserPanel():

#     def __init__(self, master):
#         naddress, background="#FFFFFF", width=50).pack() #, validatecommand= lambda: self.callback(self.tm)

        
#         contract = master.cm.instantiateContract("EXDT")
#         self.balanceLabel = tk.Label(self.user_info, text="Balance (EXDT): ", background="#EAEAEA").pack(pady=25)
#         money = 0
#         # for ad in self.subworkers:
#         #     money += round(contract.functions.balanceOf(Web3.toChecksumAddress(ad)).call()/(10**18),1)
#         money += round(contract.functions.balanceOf(Web3.toChecksumAddress(master.localconfig["ExordeApp"]["ERCAddress"])).call()/(10**18),2)
#         money += round(contract.functions.balanceOf(Web3.toChecksumAddress(master.localconfig["ExordeApp"]["MainERCAddress"])).call()/(10**18),2)
#         self.balance = tk.StringVar(self.user_info, value = money)
#         masterAddress = master.am.functions.FetchHighestMaster(master.localconfig["ExordeApp"]["ERCAddress"]).call()
#         #self.balance = tk.StringVar(self.user_info, value = round(contract.functions.balanceOf(Web3.toChecksumAddress(self.localconfig["ExordeApp"]["ERCAddress"])).call()/(10**18),1))
#         self.balanceValue = tk.Entry(self.user_info, textvariable=self.balance, background="#EAEAEA", width=50).pack()

#         contract = master.cm.instantiateContract("Reputation")
#         rep = 0
#         # for ad in self.subworkers:
#         #     rep += round(contract.functions.balanceOf(Web3.toChecksumAddress(ad)).call()/(10**18),1)
#         rep += round(contract.functions.balanceOf(Web3.toChecksumAddress(master.localconfig["ExordeApp"]["ERCAddress"])).call()/(10**18),2)
#         rep += round(contract.functions.balanceOf(Web3.toChecksumAddress(master.localconfig["ExordeApp"]["MainERCAddress"])).call()/(10**18),2)

#         self.reputationLabel = tk.Label(self.user_info, text="Reputation (REP): ", background="#EAEAEA").pack(pady=25)
#         #self.reputation = tk.StringVar(self.user_info, value = round(contract.functions.balanceOf(Web3.toChecksumAddress(masterAddress)).call()/(10**18),1))
#         self.reputation = tk.StringVar(self.user_info, value = rep)
#         self.reputationValue = tk.Entry(self.user_info, textvariable=self.reputation, background="#EAEAEA", width=50).pack()
        
#         reward = round(master.cm.instantiateContract("RewardsManager").functions.RewardsBalanceOf(master.localconfig["ExordeApp"]["MainERCAddress"]).call()/(10**18),2)
#         self.rewardLabel = tk.Label(self.user_info, text="Total Rewards (EXDT): ", background="#EAEAEA").pack(pady=25)
#         self.reward = tk.StringVar(self.user_info, value = reward)
#         self.rewardValue = tk.Entry(self.user_info, textvariable=self.reward, background="#EAEAEA", width=50).pack()
#         #tk.Button(self.user_info, text="Claim rewards", command=self.claimRewards).pack(padx= 25, pady= 25)

#         #print(self.allowance.get())
#         self.tmpAllowance = tk.BooleanVar(self.user_info)
#         self.tmpAllowance.set(master.localconfig["ExordeApp"]["SendCountryInfo"])
#         self._allowGeoCoordSending = tk.Checkbutton(self.user_info, text=" Allow sending geolocation data (Country)", variable=master.allowance, onvalue=1, offvalue=0, command=master.changeAllowanceGeo, background="#EAEAEA")
#         self._allowGeoCoordSending.pack(pady=25)
#         if(self.tmpAllowance.get() == True):
#             self._allowGeoCoordSending.select()
        
#         #self.AddressValue = tk.Label(self.user_info, text = self.localconfig["ExordeApp"]["ERCAddress"], background="#EAEAEA").pack()
#         # tk.Button(self.user_info, text="Quit", command=self.quitUserInfo).pack(anchor="se", padx= 25, pady= 25)
#         self.userFrame.pack()
#         #self.user_info.overrideredirect(1)
        
#         self.user_info.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(master))
        
#         self.user_info.mainloop()
        
    def on_closing(self, master):
        
        if general_printing_enabled:
            print("[ClaimMaster] Claiming...")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"USERPNL", "on_closing", self.status))
        
        new_val = main_wallet_
        #if(self.localconfig["ExordeApp"]["MainERCAddress"] != new_val):
        
        # with open("localConfig.json", "w") as f:
        #     json.dump(self.localconfig, f)
        if(new_val == ""):
            print("No Main Ethereum Wallet", "Please indicate your main Ethereum wallet address.")
        else:
            master.localconfig["ExordeApp"]["MainERCAddress"] = new_val
            with open('bob.txt', "rb") as file:
                pKey = file.read()
            am = master.cm.instantiateContract("AddressManager")
            increment_tx = am.functions.ClaimMaster(master.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                {
                    'from': master.localconfig["ExordeApp"]["ERCAddress"],
                    'gasPrice': master.w3.eth.gas_price,
                    'nonce': master.w3.eth.get_transaction_count(master.localconfig["ExordeApp"]["ERCAddress"]),
                }
            )
            master.tm.waitingRoom_VIP.put((increment_tx, master.localconfig["ExordeApp"]["ERCAddress"], master.pKey, True))
            
            master.updateLocalConfig()
            self.user_info.destroy()
        
# class ScrapingPanel():

#     def __init__(self, master):
#         #getting screen width and height of display
#         window_width = int((master.root.winfo_screenwidth()*20)/100)  #int((self.root.winfo_screenwidth() )/5)
#         #window_width= int((self.root.winfo_screenwidth() )/5)
        
#         window_height= int((master.root.winfo_screenheight()*30)/100)  #int((self.root.winfo_screenheight()-750)/1.75)+50  
#         if(len(master.sm.keywords) > 0):
#             #window_width *= 2
#             window_height= int((master.root.winfo_screenheight()*(30 + (5+(2.5*len(master.sm.keywords[:5]))))/100))
                
            
        
#         screen_width = master.root.winfo_screenwidth()
#         screen_height = master.root.winfo_screenheight()        
#         # find the center point
#         center_x = int(screen_width/2 - window_width / 2)
#         center_y = int(screen_height/2 - window_height / 2)        
#         # set the position of the window to the center of the screen
        
#         #♦print(self.sm.keywords)
        
#         self.sConfig = tk.Tk()
#         self.sConfig.configure(bg="#EAEAEA")
#         self.sConfig.title(" Scraping Parameters")
#         self.sConfig.iconbitmap("exd_logo.ico")
#         wi = int(window_width)
#         self.sConfig.geometry(f'{wi}x{window_height}+{center_x-10}+{center_y-35}')
#         self.sConfig.resizable(False,False)
#         self.sConfig.focus_force()
        
#         #SET PARAM FRAME
#         self.params = tk.Frame(self.sConfig, name="paramFrame", background="#EAEAEA")#, width=window_width/2
        
#         self.config = tk.Frame(self.params, background="#EAEAEA")
        
#         if(len(master.sm.keywords) > 0):
#             self.currentKeywordsFrame = tk.LabelFrame(self.config, name="currentKeywordsFrame", background="#EAEAEA", text="Active scrapings", padx=50, pady=20)
#             internalFrame1 = tk.Frame(self.currentKeywordsFrame, background="#EAEAEA")
#             for i in range(len(master.sm.keywords[:5])):
#                 miniFrame = tk.Frame(internalFrame1, background="#EAEAEA")
#                 #miniLabel = tk.Label(miniFrame, text=self.sm.keywords[i], background="#EAEAEA").pack(side = tk.LEFT, padx=5)
#                 miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=master.sm.keywords[i], onvalue=1, offvalue=1, command=partial(self.remove_item, master, master.sm.keywords[i])).pack() #,variable=var1
#                 miniFrame.pack(side = tk.TOP, anchor = tk.W) #
#             internalFrame1.pack(side=tk.LEFT, padx=5)    
            
#             internalFrame2 = tk.Frame(self.currentKeywordsFrame, background="#EAEAEA")
#             for i in range(len(master.sm.keywords[5:])):
#                 miniFrame = tk.Frame(internalFrame2, background="#EAEAEA")
#                 #miniLabel = tk.Label(miniFrame, text=self.sm.keywords[i], background="#EAEAEA").pack(side = tk.LEFT, padx=5)
#                 miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=master.sm.keywords[i+5], onvalue=1, offvalue=1, command=partial(self.remove_item, master, master.sm.keywords[i+5])).pack() #,variable=var1
#                 miniFrame.pack(side = tk.TOP, anchor = tk.W) #
#             internalFrame2.pack(side=tk.LEFT, padx=5)    
            
#             self.currentKeywordsFrame.pack(fill="both", expand="yes",pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
            
#         self.nbFrame = tk.LabelFrame(self.config, name="nbFrame", background="#EAEAEA", text="Scraped urls", padx=50, pady=20)
        
#         self.nbOne = tk.Frame(self.nbFrame, background="#EAEAEA")
#         self.keyoneLabel = tk.Label(self.nbOne, text="Urls scraped so far: ", background="#EAEAEA").pack(side = tk.TOP, padx=5)
#         self.keyoneEntry = tk.Label(self.nbOne, text=str(master.sm.nbItems), background="#EAEAEA")
#         self.keyoneEntry.pack()
#         self.nbOne.pack(pady=2.5)
        
#         self.nbFrame.pack(fill="both", expand="yes", pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
#         self.keyWordsFrame = tk.LabelFrame(self.config, name="keywordFrame", background="#EAEAEA", text="Add target", padx=50, pady=20)
        
#         self.One = tk.Frame(self.keyWordsFrame, background="#EAEAEA")
#         self.keyoneLabel = tk.Label(self.One, text="Target: ", background="#EAEAEA").pack(side = tk.LEFT, padx=5)
#         self.keyoneEntry = tk.Entry(self.One, width=25)
        
#         self.keyoneEntry.pack()
#         self.One.pack(pady=2.5)
        
#         self.keyWordsFrame.pack(fill="both", expand="yes", pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
        
#         self.config.pack()
#         self.RunButton = tk.Button(self.params, text="Start scraping", height=2, width=25, command = self.start_scraping)
#         self.RunButton.pack(fill="both", expand="yes", padx=25, pady = 5) #pady=50, padx=25
#         self.params.pack()
#         self.sConfig.bind('<Return>', self.start_scraping)
        
#         self.keyoneEntry.focus_set()
#         self.master = master
#         self.sConfig.mainloop()
    
    def start_scraping(self, event = None):

        try:
            if(len(self.master.sm.keywords) < 10):
                target = self.keyoneEntry.get()
                
                if(target != "" and target.lower() not in self.master.sm.keywords and target != None):
                    self.master.sm.keywords.append(target.lower())
                    
                elif(target.lower() in self.master.sm.keywords):
                    print("Processing info",
                                          "This target has already been taken care of..")
                else:
                    print("Processing info",
                                          "Please indicate a topic to look for.")
    
                self.sConfig.destroy()
                if(len(self.master.sm.keywords) < 10):
                    ScrapingPanel(self.master)
            else:
                print("Processing info",
                                          "{} scrapers are already running on this machine.\nPlease stop one of them before starting another.".format(len(self.master.sm.keywords)))
        except Exception as e:
            #print(e)
            pass
        
    # def remove_item(self, master, keyword):
    #     master.sm.keywords.remove(keyword)
    #     self.sConfig.destroy()
        
    #     #getting screen width and height of display
    #     window_width = int((master.root.winfo_screenwidth()*20)/100)  #int((self.root.winfo_screenwidth() )/5)
    #     #window_width= int((self.root.winfo_screenwidth() )/5)
        
    #     window_height= int((master.root.winfo_screenheight()*30)/100)  #int((self.root.winfo_screenheight()-750)/1.75)+50  
    #     if(len(master.sm.keywords) > 0):
    #         #window_width *= 2
    #         window_height= int((master.root.winfo_screenheight()*(30 + (5+(2.5*len(master.sm.keywords[:5]))))/100))
                
            
        
    #     screen_width = master.root.winfo_screenwidth()
    #     screen_height = master.root.winfo_screenheight()        
    #     # find the center point
    #     center_x = int(screen_width/2 - window_width / 2)
    #     center_y = int(screen_height/2 - window_height / 2)        
    #     # set the position of the window to the center of the screen
        
    #     #♦print(self.sm.keywords)
        
    #     self.sConfig = tk.Tk()
    #     self.sConfig.configure(bg="#EAEAEA")
    #     self.sConfig.title(" Scraping Parameters")
    #     self.sConfig.iconbitmap("exd_logo.ico")
    #     wi = int(window_width)
    #     self.sConfig.geometry(f'{wi}x{window_height}+{center_x-10}+{center_y-35}')
    #     self.sConfig.resizable(False,False)
    #     self.sConfig.focus_force()
        
    #     #SET PARAM FRAME
    #     self.params = tk.Frame(self.sConfig, name="paramFrame", background="#EAEAEA")#, width=window_width/2
        
    #     self.config = tk.Frame(self.params, background="#EAEAEA")
        
    #     if(len(master.sm.keywords) > 0):
    #         self.currentKeywordsFrame = tk.LabelFrame(self.config, name="currentKeywordsFrame", background="#EAEAEA", text="Active scrapings", padx=50, pady=20)
    #         internalFrame1 = tk.Frame(self.currentKeywordsFrame, background="#EAEAEA")
    #         for i in range(len(master.sm.keywords[:5])):
    #             miniFrame = tk.Frame(internalFrame1, background="#EAEAEA")
    #             #miniLabel = tk.Label(miniFrame, text=self.sm.keywords[i], background="#EAEAEA").pack(side = tk.LEFT, padx=5)
    #             miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=master.sm.keywords[i], onvalue=1, offvalue=1, command=partial(self.remove_item, master, master.sm.keywords[i])).pack() #,variable=var1
    #             miniFrame.pack(side = tk.TOP, anchor = tk.W) #
    #         internalFrame1.pack(side=tk.LEFT, padx=5)    
            
    #         internalFrame2 = tk.Frame(self.currentKeywordsFrame, background="#EAEAEA")
    #         for i in range(len(master.sm.keywords[5:])):
    #             miniFrame = tk.Frame(internalFrame2, background="#EAEAEA")
    #             #miniLabel = tk.Label(miniFrame, text=self.sm.keywords[i], background="#EAEAEA").pack(side = tk.LEFT, padx=5)
    #             miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=master.sm.keywords[i+5], onvalue=1, offvalue=1, command=partial(self.remove_item, master, master.sm.keywords[i+5])).pack() #,variable=var1
    #             miniFrame.pack(side = tk.TOP, anchor = tk.W) #
    #         internalFrame2.pack(side=tk.LEFT, padx=5)    
            
    #         self.currentKeywordsFrame.pack(fill="both", expand="yes",pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
            
    #     self.nbFrame = tk.LabelFrame(self.config, name="nbFrame", background="#EAEAEA", text="Scraped urls", padx=50, pady=20)
        
    #     self.nbOne = tk.Frame(self.nbFrame, background="#EAEAEA")
    #     self.keyoneLabel = tk.Label(self.nbOne, text="Urls scraped so far: ", background="#EAEAEA").pack(side = tk.TOP, padx=5)
    #     self.keyoneEntry = tk.Label(self.nbOne, text=str(master.sm.nbItems), background="#EAEAEA")
    #     self.keyoneEntry.pack()
    #     self.nbOne.pack(pady=2.5)
        
    #     self.nbFrame.pack(fill="both", expand="yes", pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
    #     self.keyWordsFrame = tk.LabelFrame(self.config, name="keywordFrame", background="#EAEAEA", text="Add target", padx=50, pady=20)
        
    #     self.One = tk.Frame(self.keyWordsFrame, background="#EAEAEA")
    #     self.keyoneLabel = tk.Label(self.One, text="Target: ", background="#EAEAEA").pack(side = tk.LEFT, padx=5)
    #     self.keyoneEntry = tk.Entry(self.One, width=25)
        
    #     self.keyoneEntry.pack()
    #     self.One.pack(pady=2.5)
        
    #     self.keyWordsFrame.pack(fill="both", expand="yes", pady=10, padx=25)#side = tk.LEFT, , fill="both", expand="yes"
        
        
    #     self.config.pack()
    #     self.RunButton = tk.Button(self.params, text="Start scraping", height=2, width=25, command = self.start_scraping)
    #     self.RunButton.pack(fill="both", expand="yes", padx=25, pady = 5) #pady=50, padx=25
    #     self.params.pack()
    #     self.sConfig.bind('<Return>', self.start_scraping)
        
    #     self.keyoneEntry.focus_set()
    #     self.sConfig.mainloop()
        
class CheckPanel():
    
    def __init__(self, master):
        
        try:            
            self.master = master
            #getting screen width and height of display
            # window_width= int((self.root.winfo_screenwidth() )/2)+75
            # window_height= int((self.root.winfo_screenheight()-400)/2)
            # screen_width = self.master.root.winfo_screenwidth()
            # screen_height = self.master.root.winfo_screenheight()        
            
            # #getting screen width and height of display
            # window_width = int((self.master.root.winfo_screenwidth()*20)/100)  #int((self.root.winfo_screenwidth() )/5)
            # if(len(self.master.val._languages) > 0):
            #     window_width *= 2
            # #window_width= int((self.root.winfo_screenwidth() )/5)
            
            # window_height= int((self.master.root.winfo_screenheight()*55)/100)  #int((self.root.winfo_screenheight()-750)/1.75)+50  
    
            # # find the center point
            # center_x = int(screen_width/2 - window_width / 2)
            # center_y = int(screen_height/2 - window_height / 2)        
            # # set the position of the window to the center of the screen
            
            # self.fScreen1 = tk.Tk()
            # self.fScreen1.configure(bg="#EAEAEA")
            # self.fScreen1.title(" Checking")
            # self.fScreen1.iconbitmap("exd_logo.ico")
            # wi = int(window_width/1.5)
            # self.fScreen1.geometry(f'{wi}x{window_height}+{center_x-10}+{center_y-35}')
            # self.fScreen1.resizable(False,False)
        

            # self.masterFormat1 = tk.Frame(self.fScreen1, background="#EAEAEA")
            
            # self.currBatchFrame = tk.LabelFrame(self.masterFormat1, background="#EAEAEA", text="Batch info", pady=15, padx=5)
            
            # self.leftBatchFrame = tk.Frame(self.currBatchFrame, background="#EAEAEA")
            
            # self.miniLabel1 = tk.Label(self.currBatchFrame, text="Current batch:", background="#EAEAEA").pack(pady=5, padx=5)
            # self.miniLabel2 = tk.Label(self.currBatchFrame, text="{}".format(self.master.val.current_batch), background="#EAEAEA") 
            # self.miniLabel2.pack(pady=5, padx=5)
            # self.miniLabel3 = tk.Label(self.currBatchFrame, text="{}/{}".format(self.master.val.current_item+1 if self.master.val.batchLength != 0 else 0, self.master.val.batchLength), background="#EAEAEA")
            # self.miniLabel3.pack(pady=5, padx=5)
            
            # self.leftBatchFrame.pack(side=tk.LEFT)
            
            # self.rightBatchFrame = tk.Frame(self.currBatchFrame, background="#EAEAEA")
            
            # self.nbBatches1 = tk.Label(self.currBatchFrame, text="Total batches:", background="#EAEAEA").pack(pady=5, padx=5)
            # self.nbBatches2 = tk.Label(self.currBatchFrame, text="{}".format(self.master.val.totalNbBatch), background="#EAEAEA").pack(pady=5, padx=5)
            print("Total Batches processed: ",int(self.master.val.totalNbBatch))
            # self.rightBatchFrame.pack(side = tk.LEFT, pady=15, padx=5)
            
            # self.currBatchFrame.pack(pady=15, padx=5, side=tk.TOP, fill="both", expand="yes") #
            
            # self.formatFrame1 = tk.LabelFrame(self.masterFormat1, background="#EAEAEA", text="Validation data", pady=15, padx=5)#
            
            for key in self.master.val._results:
                text="{}: {}%".format(key, round((self.master.val._results[key]*100)/self.master.val.nbItems, 2) if self.master.val.nbItems > 0 else "N/A")
                print("Results: ",text)
                #miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=self.sm.keywords[i], onvalue=1, offvalue=1, command=partial(remove_item, self.sm.keywords[i])).pack(side = tk.TOP, anchor=tk.W) #,variable=var1
            #     # miniFrame.pack()


            # self.formatFrame1.pack(pady=15, padx=5, side=tk.LEFT, fill="both", expand="yes")
            
            val_languages = self.master.val._languages.copy()
            
            if(len(val_languages) > 0):
                
                languages_list = dict(sorted(val_languages.items(), key = itemgetter(1), reverse = True))
                
                temp = list(set(master.sm.lang_table).intersection(languages_list))
                #tk.messagebox.showinfo("Validation Data", "Good"+",".join(temp))
                res = [languages_list[i] for i in temp]
                #tk.messagebox.showinfo("Validation Data", "Good"+",".join([str(x) for x in res]))
                
                langs = dict(zip(temp,res))
                for i in range(len(temp)):
                    langs[temp[i]] = res[i]
                    
                langs = dict(sorted(langs.items(), key = itemgetter(1), reverse = True)[:7])
                #print(langs)
                
                # self.formatFrame2 = tk.LabelFrame(self.masterFormat1, background="#EAEAEA", text="Languages", padx=5, pady=15)
                
                for k in langs.keys():
                    
                    text="{}: {}%".format( languages.get(alpha2=k).name, round((langs[k]*100)/self.master.val._results["Validated"],2))
                    print("Lang: ",k," - ",text)
                    # miniFrame = tk.Frame(self.formatFrame2, background="#EAEAEA")
                    # miniLabel = tk.Label(miniFrame, , background="#EAEAEA").pack(side = tk.LEFT, pady=5, padx=5)
                    # #miniLabel = tk.Label(miniFrame, text="{}: {}".format( languages.get(alpha2=k).name, langs[k]), background="#EAEAEA").pack(side = tk.LEFT, pady=5, padx=5)
                    # #miniEntry = tk.Checkbutton(miniFrame, background="#EAEAEA", text=self.sm.keywords[i], onvalue=1, offvalue=1, command=partial(remove_item, self.sm.keywords[i])).pack(side = tk.TOP, anchor=tk.W) #,variable=var1
                    # miniFrame.pack()
    
    
                # self.formatFrame2.pack(pady=15, padx=5, side=tk.LEFT, fill="both", expand="yes")
            
            
            # try:
            #     self.brand1 = ImageTk.PhotoImage(file="brand.png")
            #     label = tk.Label(self.masterFormat1, image=self.brand, anchor = tk.SE)
            #     label.pack()
            # except:
            #     pass
            # self.masterFormat1.pack(fill="both", expand="yes")
            # self.fScreen1.mainloop()
        except Exception as e:
            print(e)
            # self.fScreen1.destroy()
            # tk.messagebox.showinfo("Initialization error", e)

def desktop_app():
    try:
        wdg = Widget()
    except Exception as e:
        print("Init error",e)        


#print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"APP", "import", "LOADED"))           