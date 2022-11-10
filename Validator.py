# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:19:57 2022

@author: flore
"""

# import boto3
# import datetime as dt
# import json
# import os
# import random
# import re
# import requests
# import threading
# import time
# import tkinter as tk
# import tkinter.messagebox
# import transformers
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import string
# import sys
# import web3
# from web3 import Web3, HTTPProvider
# import urllib



w3 = Web3(Web3.HTTPProvider(netConfig["_urlSkale"]))


def get_blacklist(hashfile: str):
    blacklist = [x.replace('"','').strip() for x in requests.get("https://ipfs.io/ipfs/"+hashfile, allow_redirects=True).text.replace("\r","").replace("\n","")[19:-2].split(",")]
    return blacklist


        
class Validator():
    
    def __init__(self, app):

        self.app = app
        # self.localConfig = self.app.localConfig
        # self.cm = app.cm
        # self.tm = app.tm
        
        self._blacklist = get_blacklist("QmT4PyxSJX2yqYpjypyP75PR7FacBQDyES4Mdvg8m5Hrxj")        
        self._contract = self.app.cm.instantiateContract("DataSpotting")

        self._rewardsInfoLastTimestamp = 0

        self._isApproved = False
        self._isRegistered = False
        self._isRunning = False
        self._lastProcessedBatchId = 0
        self._results = {"Advertising":0,
                         "Blacklist":0,
                         "Censoring":0,
                         "Duplicates":0,
                         "Empty":0,
                         "Spam":0,
                         "Validated":0
                         }
        self._languages = dict()
        self.nbItems = 0
        self.current_batch = 0
        self.current_item = 0
        self.batchLength = 0
        self.gateWays = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/ipfs_gateways.txt").text.split("\n")
        
        now_ts = time.time()
        delay_between_rewardsInfo = 10*60 #10 min
        try:
            if general_printing_enabled:
                if ( now_ts -self._rewardsInfoLastTimestamp ) > delay_between_rewardsInfo or self._rewardsInfoLastTimestamp == 0: 
                    main_addr = self.app.localconfig["ExordeApp"]["MainERCAddress"]        
                    exdt_rewards = round(self.app.cm.instantiateContract("RewardsManager").functions.RewardsBalanceOf(main_addr).call()/(10**18),2)
                    rep_amount = round(self.app.cm.instantiateContract("Reputation").functions.balanceOf(main_addr).call()/(10**18),2)
                    print("[CURRENT REWARDS & REP] Main Address {}, REP = {} and EXDT Rewards = {} ".format(str(main_addr), rep_amount, exdt_rewards))
                    self._rewardsInfoLastTimestamp = now_ts
        except:
            time.sleep(2)
            pass

        if validation_printing_enabled:
            print("[Validation] sub routine instancied")
        self.totalNbBatch = 0
        
        # tokenizer = AutoTokenizer.from_pretrained("alonecoder1337/bert-explicit-content-classification")
        # model = AutoModelForSequenceClassification.from_pretrained("alonecoder1337/bert-explicit-content-classification")
        # self._explicitPipeline = transformers.pipeline("text-classification",model=model,tokenizer=tokenizer, return_all_scores=True)
        
        try:
            self.spammerList = self.downloadFile(self.app.cm.instantiateContract("ConfigRegistry").functions.get("spammerList").call())["spammers"]
        except:
            self.spammerList = self.downloadFile("QmStbdSQ8KBM72uAoqjcQEhJanhq2J8J2Q3ReijwxYFzme")["spammers"]
        
        try:
            print("\t[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"REGISTERING", "-", "Registering worker online for work.".format(len(fileList))))
            self.register()
        except Exception as e:
            #print(e)
            self._isRegistered = False
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "__init__", "COMPLETE")) 
        self.checkThread = threading.Thread(target=self.manage_checking)
        self.checkThread.daemon = True
        self.checkThread.start()
        
    def threadHunter(self, thread):
        
        time.sleep(10)
        #print(thread, "out of", threading.active_count())
        if(self.status == "DOWNLOADING"):
            #print("Trying to kill thread", thread.ident, "-", thread.native_id)
            del thread
            try:
                self.send_votes(self.current_batch, [], "DLERROR", 0, 0)
            except:
                pass
        else:
            pass
            #print("Thread", thread.ident, "-", thread.native_id, "on", self.status)

    def manage_checking(self):
        
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "manage_checking", "RUNNING")) 
        i = 0
        while True:
            
            # if(self._isRunning):  

            #     rep += round(contract.functions.balanceOf(Web3.toChecksumAddress(ad)).call()/(10**18),1) 

            # else:
            if validation_printing_enabled:
                print("[Validation] Lauching the check content routine")
            exec("x{} = threading.Thread(target=self.check_content)".format(i))
            exec("x{}.daemon = True".format(i))
            exec("x{}.start()".format(i))
            # exec("y = threading.Thread(target=self.threadHunter, args=(x{},))".format(i))
            # exec("y.start()")
            #self._isRunning = True
            time.sleep(60*3.5)
            i += 1
            if i >= 250000:
                i = 0
            # if(self.status == "DOWNLOADING"):
            #     print("Trying to kill thread")
            #     del x
                
        # while self._isRunning:
            
        #     try:
                
        #         x = threading.Thread(target=self.check_content)
        #         x.start()
        #         #self.check_content()
        #         time.sleep(60)
        #     except:
        #         time.sleep(60)
                
        
    def register(self):
        
        if validation_printing_enabled:
            print("[Validation] DataSpotting contract instanciated")
        
        self._isApproved = self.app.cm.StakeManagement(self.app.tm) or self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call()
        self._isRegistered = self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call()
        
        
        if(self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call() == False):
        
            if(self._isApproved == False and self._isRegistered == False):
                
                #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "register", "REGISTERING")) 
                trials = 0
                
                while(self._isApproved == False or trials < 5):
                    self._isApproved = self.app.cm.readStake()
                    if(self._isApproved == True):
                        
                        increment_tx = self._contract.functions.RegisterWorker().buildTransaction(
                            {
                                'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                'gasPrice': w3.eth.gas_price,
                                'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                            }
                        )
                        
                        self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                        
                        time.sleep(30)
                        
                        _isRegisteredTrials = 0
                        while(_isRegisteredTrials < 5):
                            
                        
                            if(self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call() == True):
                                self._isRegistered = True
                                break
                            else:
                                _isRegisteredTrials += 1
                                time.sleep(30)
                        if(_isRegisteredTrials == 5 and self._isRegistered == False):
                            print("Initialization error",
                                                      "Something went wrong while registering your worker address on the Validation Worksystem.\nPlease try restarting your application.")
                        
                    else:
                        
                        self.app.cm.StakeManagement(self.app.tm)
                        trials += 1
                        time.sleep(30)
    
                if(trials >= 5 and self._isRegistered == False):
                    print("Initialization error",
                              "Something went wrong while registering1 your worker address on the Validation Worksystem.\nPlease try restarting your application.")
                    os._exit(0)
                    
            elif(self._isApproved == True and self._isRegistered == False):
                
                increment_tx = self._contract.functions.RegisterWorker().buildTransaction(
                    {
                        'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                        'gasPrice': w3.eth.gas_price,
                        'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                    }
                )
                
                self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))            
                
                if(self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call() == False):
                    increment_tx = self._contract.functions.RegisterWorker().buildTransaction(
                        {
                            'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                            'gasPrice': w3.eth.gas_price,
                            'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                        }
                    )
                    
                    self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                    
                    time.sleep(30)
                    
                    _isRegisteredTrials = 0
                    while(_isRegisteredTrials < 5):
                        
                    
                        if(self._contract.functions.isWorkerRegistered(self.app.localconfig["ExordeApp"]["ERCAddress"]).call() == True):
                            self._isRegistered = True
                            
                            break
                        else:
                            _isRegisteredTrials += 1
                            time.sleep(30)
                    if(_isRegisteredTrials == 5 and self._isRegistered == False):
                        print("Initialization error",
                                                  "Something went wrong while registering your worker address on the Validation Worksystem.\nPlease try restarting your application.")
                        os._exit(0)
                        
            elif(self._isRegistered == True):
                return
         
    def downloadFile(self, hashname: str):
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
            'pinata_api_key': "19d2b24b75ad7253aebf", 
            'pinata_secret_api_key': "f69150422667f79ce5a7fb0997bfdbb3750894cd1734275f77d867647e4f3df4",
            'Connection':'close'
        }

        
        
        trials = 0
        
        for gateway in ["https://ipfs.filebase.io/ipfs/",
                       "https://ipfs.eth.aragon.network/ipfs/",
                       "https://api.ipfsbrowser.com/ipfs/get.php?hash="]:
            
            url = gateway + hashname
            
            trials = 0
            while trials < 5:
                try:
                    r = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=3) #
                    if(r.status_code == 200):
                        try:
                            return r.json()
                        except:
                            pass
                    else:
                        #print(r.__dict__)
                        trials += 1
                except Exception as e:
                    #print(e)
                    trials += 1
                if(trials >= 5):
                    break
            if(trials == 5):
                break
                #print("Couldn't download file", hashname)
        return None  
            
        
    
    def get_content(self):
        
        self.status = "DOWNLOADING"
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
            #'pinata_api_key': "19d2b24b75ad7253aebf", 
            #'pinata_secret_api_key': "f69150422667f79ce5a7fb0997bfdbb3750894cd1734275f77d867647e4f3df4" 
        }
        
        status = ""
        max_trials_ = 2
        timeout_ = 3

            
        
        if detailed_validation_printing_enabled:
            print("[Validation] Checking if worker is registered already")

        str_my_address = self.app.localconfig["ExordeApp"]["ERCAddress"]
        
        # if validation_printing_enabled:
        #     print("[Validation] Worker Address = ",str_my_address)

        for trial in range(max_trials_):  
            try:                    
                if(self._contract.functions.isWorkerRegistered(str_my_address).call() == False):
                    
                    if validation_printing_enabled:
                        print("[Validation] Worker {} Not registered".format(str_my_address))
                    self.register()
                    print("\t[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"REGISTERING", "-", "Registering worker online for work.".format(len(fileList))))
                else:
                    if validation_printing_enabled:
                        print("[Validation] Worker {} already registered".format(str_my_address))
                break
            except:
                time.sleep(3)
                pass


        try:
            _isNewWorkAvailable = self._contract.functions.IsNewWorkAvailable(self.app.localconfig["ExordeApp"]["ERCAddress"]).call()
        except:
            _isNewWorkAvailable = False
            
        _isNewWorkAvailable = "True"
        # print("overriding for debug: _isNewWorkAvailable = ",_isNewWorkAvailable)

        if(_isNewWorkAvailable == "False"): 
            if validation_printing_enabled:
                print("[Validation] No new work, standby.")
            return None, []
        else:
            if validation_printing_enabled:
                print("[Validation] New Work Available Detected.")
                print("[Validation] Fetching Work Batch ID")
            try:
                for trial in range(max_trials_):  
                    try:
                        gateways =  requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/ipfs_gateways.txt").text.split("\n")[:-1]
                    except:
                        time.sleep(3)
                        pass
                nb_gateways = len(gateways)
                
                
                for trial in range(max_trials_):  
                    try:                        
                        batchId = int(self._contract.functions.GetCurrentWork(self.app.localconfig["ExordeApp"]["ERCAddress"]).call())
                    except:
                        time.sleep(2*trial)
                        batchId = 0
                        pass
                    
                if(batchId > self._lastProcessedBatchId and batchId > self.current_batch):
                    
                    self.current_batch = batchId #moved up

                    dataBlocks = list()
                    try:
                        fileList = self._contract.functions.getIPFShashesForBatch(batchId).call()
                    except:
                        fileList = []
                        
                    if validation_printing_enabled:
                        print("\t[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"DATA BATCH VALIDATION", "Batch ID = {}".format(batchId), "PROCESSING {} batch files.".format(len(fileList))))
                    
                    for i in range(len(fileList)):
                        file = fileList[i]
                        
                        if detailed_validation_printing_enabled:
                            print("\t\tDownloading IPFS sub-file -> ",file," ... ", end='')
                    #for file in fileList:
                        #print("\nFetching IPFS file = ",file)    
                        isOk = False
                        # retry all gateways twice, after pause of 10s in between, before giving up on a batch
                        for trial in range(max_trials_):    
                            _used_timeout = timeout_*(1+trial)
                            #print("trial n°",trial,"/",(max_trials_-1))
                            ## initialize the gateway loop
                            gateway_cursor = 0 
                            ### iterate a trial of the download over all gateways we have
                            for gateway_ in gateways:
                                _used_gateway = gateways[gateway_cursor]
                                _used_gateway = random.choice(gateways)
                                try:
                                    _endpoint_url = _used_gateway+file
                                    #content = urllib.request.urlopen(_endpoint_url, timeout=_used_timeout)
                                    time.sleep(1)
                                    try:
                                        content = requests.get(_endpoint_url, headers=headers, allow_redirects=True, stream=True, timeout=3)
                                        if detailed_validation_printing_enabled:
                                            print("  downloaded.")
                                    except Exception as e:
                                        # print(e)
                                        
                                        if detailed_validation_printing_enabled:
                                            print(",", end='')
                                    try:
                                        content = content.json()
                                        content = content["Content"]
                                    except Exceptin as e:
                                        #print(e)
                                        #print("\t\t--failed to open the content")
                                        content = None                
                                    for item in content:
                                        try:
                                            dataBlocks.append(item)
                                        except Exception as e:
                                            #print("\tDataBlock error", e, item)
                                            pass
                                    #print("\t",len(content),"Items added")
                                    if(len(content)>0):                    
                                        isOk = True
                                    time.sleep(1)
                                    break
                                except Exception as e:
                                    gateway_cursor += 1
                                    if gateway_cursor>=nb_gateways:
                                        #print("\t----Tried all gateways")
                                        break     
                                ## Break from gateway loop if we got the file
                                if isOk:
                                    break        
                                #time.sleep(1)
                            ## Break from trial loop if we got the file
                            if isOk:
                                break
                            
                    if detailed_validation_printing_enabled:
                        print("\tData Batch files fetched sucessfully.")
                                        
                    self._lastProcessedBatchId = batchId

                    return batchId, dataBlocks
                    
                    
            except Exception as e:
                print(e)
                pass
                    
                    
            return None, []
            
    
    def isSpamContent(self, text):
        
        if(text in self.spammerList):
            return True
        else:
            return False
            
    def isExplicitContent(self, text):
        #print(text)
        return False
    
    def isAdvertisingContent(self, text, debug_=False):
        # regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        regex = r"(https?://[^\s]+)"
        if debug_: 
            print("isAdvertisingContent debug ",  regex)
        
        url_founds = re.findall(regex,text)
        if debug_: 
            print("URL Found in content = ",url_founds)
            print("Number of URL Found in content = ",len(url_founds))
        if(len(url_founds) >= 4):
            
            if debug_: 
                print("isAdvertisingContent ADVERTISING DETECTED")
            return True
        else:
            return False
        
    def generateFileName(self):
        random.seed(random.random())
        baseSeed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=256))
        fileName = baseSeed + '.txt'
        return fileName
    
    def filebase_download(self, bucketName, keyName):

        s3 = boto3.client(
            's3',
            endpoint_url = 'https://s3.filebase.com',
            region_name='us-east-1',
            aws_access_key_id='24C83682E3758DA63DD9',
            aws_secret_access_key='B149EQGd1WwGLpuWHgPGT5wQ5OqgXPq3AOQtTeBr'
        )
        keyName = "QmdjDzRZGZEVzNnnViRzPgMLSjrTC12CH4usqqGCc3UBMc"
        # bucketName = "exorde-spotdata-1"
        response = s3.get_object(Bucket = bucketName, Key=keyName)

        return response
    
    def filebase_upload(self, content: str, bucket_name: str):
        
        s3 = boto3.resource(
            's3',
            endpoint_url = 'https://s3.filebase.com',
            region_name='us-east-1',
            aws_access_key_id='24C83682E3758DA63DD9',
            aws_secret_access_key='B149EQGd1WwGLpuWHgPGT5wQ5OqgXPq3AOQtTeBr'
        )
        response = s3.Object(bucket_name, self.generateFileName()).put(Body=content)

        return response["ResponseMetadata"]["HTTPHeaders"]['x-amz-meta-cid']
        
    def isCommitPeriodActive(self, batchId):

        _secondsToWait = 5
        _isPeriodActive = False
        
        for i in range(5):
            
            try:
            
                _isPeriodActive = self._contract.functions.commitPeriodActive(batchId).call()
                if(_isPeriodActive == True):
                    break
            
            except:
                
                
                time.sleep(_secondsToWait*i)
                
        return _isPeriodActive
    
    def isRevealPeriodActive(self, batchId):
        
        _secondsToWait = 5
        _isPeriodActive = False
        
        for i in range(6):
            
            try:
            
                _isPeriodActive = self._contract.functions.revealPeriodActive(batchId).call()
                if(_isPeriodActive == True):
                    break
            
            except:
                
                
                time.sleep(_secondsToWait*i)
                
        return _isPeriodActive
    
    def send_votes(self, batchId, results, status, batchResult, randomSeed):
        
        self.status = "VOTING"
        
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VOTING", "send_votes", " BatchStatus({})".format(batchResult)))
        
        
        _isUploaded = False
        _uploadTrials = 0
        
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"UPLOADING FILE", "send_votes", " BatchStatus({})".format(batchResult)))
        res = ""
        
        while(_isUploaded == False or _uploadTrials < 5):
            if(res == ""):
                try:
                    configRegistry_ = self.app.cm.instantiateContract("ConfigRegistry")
                    
                    trials_ = 0
                    bucket_to_upload = "exorde-spotdata-1"
                    while True:
                        try:
                            # print("bucket_to_upload try")
                            bucket_to_upload = configRegistry_.functions.get("SpotcheckBucket").call()
                            break
                        except:
                            # print("fail spotcheck bucket recup, retry")
                            trials_ += 1
                            time.sleep(2)
                            if trials_ > 5:
                                break
                            
                    trials_ = 0
                    while True:
                        try:
                            if validation_printing_enabled:
                                print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"FILE UPLOAD ATTEMPT ", "send_votes", " Bucket({})".format(bucket_to_upload)))
                            res = self.filebase_upload(json.dumps({"Content":results}, indent=4, sort_keys=True, default=str), bucket_to_upload )
                            break
                        except:
                            if validation_printing_enabled:
                                print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"FILE UPLOAD RETRY ", "send_votes", " Bucket({})".format(bucket_to_upload)))
                            trials_ += 1
                            time.sleep(2)
                            if trials_ > 5:
                                break

                    _isUploaded = True
        
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"FILE UPLOADED ", "send_votes", " Bucket({})".format(bucket_to_upload)))
                    break
                except:
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"FILE UPLOAD FAILED ", "send_votes", " Bucket({})".format(bucket_to_upload)))
                    _uploadTrials += 1
                    time.sleep(5*(_uploadTrials+1))
                if(_uploadTrials >= 5):
                    break
            else:
                break
            if(_uploadTrials >= 5):
                break
            
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"UPLOADING DONE", "send_votes", " BatchStatus({})".format(batchResult)))

        try:    
            if(res != "" or status != "Success"):
                if(self._contract.functions.isWorkerAllocatedToBatch(batchId, self.app.localconfig["ExordeApp"]["ERCAddress"])): #here
                
                    try:
                        _didCommit = self._contract.functions.didCommit(self.app.localconfig["ExordeApp"]["ERCAddress"], batchId).call()
                    except:
                        _didCommit = False
                    
                    if detailed_validation_printing_enabled:
                        print("\t[Validation - L2] didCommit = ",_didCommit)
                
                    if(_didCommit == False):
                        
                        if detailed_validation_printing_enabled:
                            print("\t[Validation - L2] didCommit False loop => ")
                        
                        try:
                            _commitPeriodOver = self._contract.functions.commitPeriodOver(batchId).call()
                        except:
                            _commitPeriodOver = False
                            
                        if detailed_validation_printing_enabled:
                            print("\t[Validation - L2] _commitPeriodOver = ",_commitPeriodOver)
                        if(_commitPeriodOver == False):
                            drop = False
                            try:
                                
                                while True:
                                    
                                    try:
                                        
                                        try:
                                            _commitPeriodActive = self._contract.functions.commitPeriodActive(batchId).call()
                                        except:
                                            _commitPeriodActive = False
                                            
                                        if detailed_validation_printing_enabled:
                                            print("\t[Validation - L2] _commitPeriodActive({}) = ".format(batchId),_commitPeriodActive)
                                        
                                        if(_commitPeriodActive == True):
                                            if detailed_validation_printing_enabled:
                                                print("\t[Validation - L2] _commitPeriodActive is true")
                                            drop = False
                                            break
                                        else:
                                            time.sleep(5)
                                            if detailed_validation_printing_enabled:
                                                print("\t[Validation - L2] _commitPeriodActive  false so wait 5s")
                                            
                                            try:
                                                _commitPeriodOver = self._contract.functions.commitPeriodOver(batchId).call()
                                            except:
                                                _commitPeriodOver = False
                                                
                                            if detailed_validation_printing_enabled:
                                                print("\t[Validation - L2] _commitPeriodOver  false so wait 5s")
                                            if(_commitPeriodOver == True):
                                                drop = True
                                                break
                                    except:
                                        time.sleep(30)
                                    
                            except Exception as e:
                                #print(e)
                                pass

                            if(drop == False):
                                hasCommitted = False
                                while(hasCommitted == False):
                                    if(hasCommitted == False):
                                        try:
                                            increment_tx = self._contract.functions.commitSpotCheck(batchId, self._contract.functions.getEncryptedStringHash(res, randomSeed).call(), self._contract.functions.getEncryptedHash(batchResult, randomSeed).call(), len(results), status).buildTransaction(
                                                {
                                                    'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                                    'gasPrice': w3.eth.gas_price,
                                                    'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                                                }
                                            )
                                            self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                                            hasCommitted = True

                                            if validation_printing_enabled:
                                                print("\t[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "send_votes", "SUBMISSION & VOTE ENCRYPTED - Commited({})".format(batchId)))
                                            

                                            break
                                        except Exception as e:
                                            time.sleep(30)
                                    else:
                                        break
                                
                                while True:
                                    try:
                                        
                                        try:
                                            _revealPeriodActive = self._contract.functions.revealPeriodActive(batchId).call()
                                        except:
                                            _revealPeriodActive = False
                                            
                                        if detailed_validation_printing_enabled:
                                            print("\t[Validation - L2] _revealPeriodActive = ",_revealPeriodActive)
                                        if(_revealPeriodActive == True):
                                            #print("Reveal period open")
                                            break
                                        else:
                                            time.sleep(10)
                                    except:
                                        time.sleep(30)
                                    
                                
                                while True:
                                    
                                    try:
                                        _revealPeriodOver = self._contract.functions.revealPeriodOver(batchId).call()
                                    except:
                                        _revealPeriodOver = False
                                    
                                    if detailed_validation_printing_enabled:
                                        print("\t[Validation - L2] _revealPeriodOver = ",_revealPeriodOver)

                                    if(_revealPeriodOver == False):
                                        if detailed_validation_printing_enabled:
                                            print("\t[Validation - L2] _revealPeriodOver FALSE loop ")
                                        try:
                                            
                                            try:
                                                _didReveal = self._contract.functions.didReveal(self.app.localconfig["ExordeApp"]["ERCAddress"], batchId).call()
                                            except:
                                                _didReveal = False
                                            if detailed_validation_printing_enabled:
                                                print("\t[Validation - L2] didReveal ",_didReveal)
                                                
                                            if(_didReveal == False):
                                                
                                                try:
                                                    _didCommit = self._contract.functions.didCommit(self.app.localconfig["ExordeApp"]["ERCAddress"], batchId).call()
                                                except:
                                                    _didCommit = True

                                                if detailed_validation_printing_enabled:
                                                    print("\t[Validation - L2] _revealPeriodOver _didCommit ",_didCommit)
                                                    
                                                if(_didCommit == True):
                                                    hasRevealed = False
                                                    while(hasRevealed == False):
                                                        try:
                                                            increment_tx = self._contract.functions.revealSpotCheck(batchId, res, batchResult, randomSeed).buildTransaction(
                                                                {
                                                                    'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                                                    'gasPrice': w3.eth.gas_price,
                                                                    'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                                                                }
                                                            )
                                                            self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                                                            hasRevealed = True
                                                            
                                                            if validation_printing_enabled:
                                                                print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "send_votes", "SUBMISSION & VOTE - Revealed ({})".format(batchId)))

                                                            time.sleep(5)
                                                            self._lastProcessedBatchId = batchId
                                                            break
                                                        except Exception as e:
                                                            pass
                                                            #print(e)
                                                    break
                                        except Exception as e:
                                            break
                                            #print(e)
                                    else:
                                        break   
                                
                                
                    else:
                        print("\t[Validation - L2] waiting 5s")
                        time.sleep(5)
                else:
                    print("\t[Validation - L2] Worker not allocated the batch! [Error]")

        except Exception as e:
            print(e)
            pass
        #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "send_votes", "VOTED({})".format(batchId)))
    
    def process_batch(self, batchId, documents):
        
        if(batchId != None):
            
            if validation_printing_enabled:
                print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "process_batch", "PROCESSING DATA({})".format(batchId)))
        
        try:
            randomSeed = random.randint(0,999999999)
            results = dict()
            ram = list()
            
            if(len(documents) > 0):
                #print("Checker on batch", batchId)
                try:
                    
                    batchResult = 1
                    for i in range(len(documents)):
                        if i%50 == 0 and detailed_validation_printing_enabled:
                                print("\t\t -> Web Content item ",int(i)," / ",len(documents))

                        # if i >= 79:
                        #     print("\t\t ******************Fucking item:")
                        
                        
                        try:
                            self.current_item = i                            
                            document = documents[i]
                        except:
                            document = None
                        # print()
                        # print(document)
                        #print()

                        try:
    
                            response = 1
                            if(document != None):
                                # if i >= 79:
                                #     print("Document is not none")
                                #     print("document length = ",len(document))
                                #     print("\nDocument = ",document,"\n")
                                
                                # if i >= 79:
                                #     print("Opening content & replacing slashes...")

                                document["item"]["Content"] = document["item"]["Content"].replace('"','\"')

                                # if i >= 79:
                                #     print("done...")
                                #     print("Content = ",document["item"]["Content"])
    
                                try:
                                    debug_toggle = False
                                    # if i >= 79:
                                    #     print("A...")
                                    #     debug_toggle = True

                                    if(self.isAdvertisingContent(str(document["item"]["Content"]), debug_=debug_toggle)):
                                        
                                        # if i >= 79:
                                        #     print("A2...")
                                        self._results["Advertising"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("B...")

                                    #print("B")
                                    if (document["item"]["Content"].strip() in ("[removed]", "[deleted]", "[citation needed]", "", "None")):
                                        self._results["Empty"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("C...")
                                    
                                    if(self.isExplicitContent(document["item"]["Content"])):
                                        self._results["Censoring"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("D...")
                                    
                                    if(document["item"]["Url"] in self._blacklist or document["item"]["DomainName"] in self._blacklist):
                                        self._results["Blacklist"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("e...")
                                    
                                    if(self.isSpamContent(document["item"]["Author"])):
                                        self._results["Spam"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("f...")
                                    
                                    if(document["item"]["Url"] in ram):
                                        self._results["Duplicates"] += 1
                                        response = 0

                                    # if i >= 79:
                                    #     print("g...")
                                    
                                    if(response == 1):
                                        self._results["Validated"] += 1
                                        

                                        # if i >= 79:
                                        #     print("response = 1...")
                                    
                                        if(document["item"]["Language"] not in self._languages):
                                            self._languages[document["item"]["Language"]] = 1
                                        else:
                                            self._languages[document["item"]["Language"]] += 1
                                            
                                        # if i >= 79:
                                        #     print("pre append to results")

                                        # results.append(document) 
                                        results[document["item"]["Url"]] = document
                                        
                                        # if i >= 79:
                                        #     print("appened.")

                                        ram.append(document["item"]["Url"])
                                    
                                    self.nbItems += 1
                                except Exception as e:
                                    print("Exception during processing: ",e)
    
                                    response = 0
                                    self.nbItems += 1
                        except Exception as e:
                
                            print("Exception catched = ",e)
                            self.nbItems += 1
                            response = 0        
                            
                    status = "Success"
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "Processing Status:", " [{}] ".format(status)))   
                    # print("[Validation] Batch processing status = ",status)
                    
                    x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                    x.daemon = True
                    x.start()
                except Exception as e:
                    #print("Bob2",e)
                    status = "Failure"
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "Processing Status:", " [{}] ".format(status)))   
                    # print("[Validation] Batch processing status = ",status)
                    batchResult = 0
                    x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                    x.daemon = True
                    x.start()
                    #self.send_votes(batchId, results, status, batchResult, randomSeed)
                    
            elif(len(documents) == 0):   
                status = "NoData"
                batchResult = 0
                x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                x.daemon = True
                x.start()
                #self.send_votes(batchId, results, status, batchResult, randomSeed)
        except Exception as e:
            #print(e)
            pass
            
    def check_content(self, doc:str = ""):
        
        #while self._isRunning:
            
        try:
            
            now_ts = time.time()
            delay_between_rewardsInfo = 10*60 #10 min
            try:
                if general_printing_enabled:
                    if ( now_ts -self._rewardsInfoLastTimestamp ) > delay_between_rewardsInfo or self._rewardsInfoLastTimestamp == 0: 
                        main_addr = self.app.localconfig["ExordeApp"]["MainERCAddress"]        
                        exdt_rewards = round(self.app.cm.instantiateContract("RewardsManager").functions.RewardsBalanceOf(main_addr).call()/(10**18),2)
                        rep_amount = round(self.app.cm.instantiateContract("Reputation").functions.balanceOf(main_addr).call()/(10**18),2)
                        print("[CURRENT REWARDS & REP] Main Address {}, REP = {} and EXDT Rewards = {} ".format(str(main_addr), rep_amount, exdt_rewards))
                        self._rewardsInfoLastTimestamp = now_ts
            except:
                time.sleep(2)
                pass
            
            batchId, documents = self.get_content()
            
            #print("Protocol told me to do the batch", batchId)
            if(batchId != None):
                
                if(batchId != None and batchId >= self.current_batch):
                    #self._isRunning = True
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"VALIDATION", "check_content", "PROCESSING({})".format(batchId)))
                    try:
                        # self.current_batch = batchId
                        # self._lastProcessedBatchId = batchId
                        self.totalNbBatch += 1
                        self.batchLength = len(documents)
                        
                        self.process_batch(batchId, documents)
                        self._lastProcessedBatchId = batchId
                        self._isRunning = False
                    except Exception as e:
                        #print(e)
                        self._isRunning = False
                    #sys.exit()
                else:
                    #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "check_content", "NO NEW JOB".format(batchId)))
                    self.status = "OLDJOB"
            else:
                self.status = "NOJOB"
                
        except Exception as e:
            #print("Bob", e)
            self._isRunning = False
            #sys.exit()
                
            # cont = self.app.cm.instantiateContract("DataSpotting")
            # increment_tx = cont.functions.UnregisterWorker().buildTransaction(
            #     {
            #         'from': self.localconfig["ExordeApp"]["ERCAddress"],
            #         'gasPrice': w3.eth.gas_price,
            #         'nonce': w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"]),
            #     }
            # )
            # self.app.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))
                
            
#print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"CHECKER", "import", "LOADED")) 
