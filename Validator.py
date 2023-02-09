# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 14:20:53 2022

@author: florent, mathias
Exorde Labs
"""



def get_blacklist(hashfile: str):
    blacklist = [x.replace('"','').strip() for x in requests.get("https://ipfs.io/ipfs/"+hashfile, allow_redirects=True).text.replace("\r","").replace("\n","")[19:-2].split(",")]
    return blacklist

ramholder_validation = None

default_gas_price = 100_000 # 100000 wei or 0.0001


class Validator():
    
    def __init__(self, app):
        self.app = app

        RAM_HOLDER_AMOUNT_VALIDATION = 800_000_000
        self.ramholder_validation = bytearray(RAM_HOLDER_AMOUNT_VALIDATION)
        
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
        
        if general_printing_enabled:
            print("[Validation {}] IPFS gateways fetched".format(dt.now()))
        

        now_ts = time.time()
        delay_between_rewardsInfo = 10*60 #2 min
        try:
            main_addr = self.app.localconfig["ExordeApp"]["MainERCAddress"]       
            time.sleep(0.5) 
            to = 10
            # mainnet_config_github_url = 'https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/NetworkConfig.txt'
            # testnet_config_github_url = 'https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt'
            # mainnet_contracts = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ContractsAddresses.txt", timeout=to).json()
            # testnet_contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()

            # netConfig_mainnet = requests.get(mainnet_config_github_url, timeout=30).json()
            # netConfig_testnet = requests.get(testnet_config_github_url, timeout=30).json()

            # w3_mainnet = Web3(Web3.HTTPProvider(netConfig_mainnet["_urlSkale"]))
            # w3_testnet = Web3(Web3.HTTPProvider(netConfig_testnet[sync_node_id]))

            # abi_rep = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/Reputation.sol/Reputation.json", timeout=to).json()

            # base_rep_archive_url_ = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/archives/partial_testnets/base_reputation_amount.json"
            base_rep_archive_url_ = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"

            base_rep_archive_ = requests.get(base_rep_archive_url_, timeout=to).json()
            rep_amount_base_archive = 0
            if main_addr in base_rep_archive_:
                rep_amount_base_archive = base_rep_archive_[main_addr]

            # contract_mainnet = w3_mainnet.eth.contract(mainnet_contracts["Reputation"], abi=abi_rep["abi"])
            # contract_testnet = w3_testnet.eth.contract(testnet_contracts["Reputation"], abi=abi_rep["abi"])

            # rep_amount_mainnet = round(contract_mainnet.functions.balanceOf(main_addr).call()/(10**18),4)
            # rep_amount_testnet = round(contract_testnet.functions.balanceOf(main_addr).call()/(10**18),4)

            # rep_amount = round(rep_amount_testnet + rep_amount_mainnet + rep_amount_base_archive,4)
            # rep_amount = round(rep_amount_testnet + rep_amount_base_archive,4)
            rep_amount = round(rep_amount_base_archive,4)


            # rep_amount = round(self.app.cm.instantiateContract("Reputation").functions.balanceOf(main_addr).call()/(10**18),2)
            print("[CURRENT REWARDS & REP] Main Address {}, REP Rewards = {}, Time of snapshot = {} (Source: Testnet Leaderboard)".format(str(main_addr), rep_amount, dt.now()))
            self._rewardsInfoLastTimestamp = now_ts
        except Exception as e:
            print(e)
            time.sleep(2)
            pass

        if validation_printing_enabled:
            print("[Validation {}] sub routine instancied".format(dt.now()))
        self.totalNbBatch = 0
        
        # tokenizer = AutoTokenizer.from_pretrained("alonecoder1337/bert-explicit-content-classification")
        # model = AutoModelForSequenceClassification.from_pretrained("alonecoder1337/bert-explicit-content-classification")
        # self._explicitPipeline = transformers.pipeline("text-classification",model=model,tokenizer=tokenizer, return_all_scores=True)
        
        try:
            time.sleep(0.2)
            self.spammerList = self.downloadFile(self.app.cm.instantiateContract("ConfigRegistry").functions.get("spammerList").call())["spammers"]
        except:
            self.spammerList = self.downloadFile("QmStbdSQ8KBM72uAoqjcQEhJanhq2J8J2Q3ReijwxYFzme")["spammers"]
        

        try:
            self.register()
        except Exception as e:
            print("REGISTERING ERROR:", e)
            self._isRegistered = False
        #print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"CHECKER", "__init__", "COMPLETE")) 
        self.checkThread = threading.Thread(target=self.manage_checking)
        self.checkThread.daemon = True
        self.checkThread.start()

        
        if validation_printing_enabled:
            print("[Validation {}] sub routine initialized".format(dt.now()))

        
    def threadHunter(self, thread):
        
        time.sleep(10)
        if(self.status == "DOWNLOADING"):
            del thread
            try:
                self.send_votes(self.current_batch, [], "DLERROR", 0, 0)
            except:
                pass
        else:
            pass

    def manage_checking(self):
        i = 0
        while True:            
            if validation_printing_enabled:
                print("[Validation {}] Lauching the check content routine".format(dt.now()))
            exec("x{} = threading.Thread(target=self.check_content)".format(i))
            exec("x{}.daemon = True".format(i))
            exec("x{}.start()".format(i))
            time.sleep(60)
            i += 1
            if i >= 250000:
                i = 0
                
                
        
    def register(self):
        worker_address = self.app.localconfig["ExordeApp"]["ERCAddress"]
        
        increment_tx = self._contract.functions.RegisterWorker().buildTransaction(
            {
                'from': worker_address,
                'gasPrice': default_gas_price,
                'nonce': w3.eth.get_transaction_count(worker_address),
            }
        )
        
        print("Putting Register Tx in WaitingRoom")
        self.app.tm.waitingRoom_VIP.put((increment_tx, worker_address, self.app.pKey))

         
    def downloadFile(self, hashname: str):        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
            'Connection':'close'
        }

        trials = 0        
        for gateway in [ "http://ipfs-gateway.exorde.network/ipfs/",
                         "https://w3s.link/ipfs/",
                         "https://ipfs.io/ipfs/",
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
                    trials += 1
                    time.sleep(1+trials)
                if(trials >= 5):
                    break
            if(trials == 5):
                break
                #print("Couldn't download file", hashname)
        return None  

    
    def get_content(self):
        
        self.status = "DOWNLOADING"
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'
        }
        
        status = ""
        max_trials_ = 2
        timeout_ = 3
                    
        if detailed_validation_printing_enabled:
            print("[Validation {}] Checking if worker is registered already".format(dt.now()))

        str_my_address = self.app.localconfig["ExordeApp"]["ERCAddress"]
        
        for trial in range(max_trials_):  
            try:                    
                time.sleep(2)
                if self._contract.functions.isWorkerRegistered(str_my_address).call() == False:
                    
                    if validation_printing_enabled:
                        print("[Validation {}] Worker {} Not registered".format(dt.now(),str_my_address))
                    self.register()
                    print("\t[{}]\t{}\t{}\t\t{}".format(dt.now(),"REGISTERING", "-", "Registering worker online for work.".format(len(fileList))))
                else:
                    if validation_printing_enabled:
                        print("[Validation {}] Worker {} already registered".format(dt.now(),str_my_address))
                break
            except:
                time.sleep(3)
                pass


        try:
            time.sleep(1)
            _isNewWorkAvailable = self._contract.functions.IsNewWorkAvailable(self.app.localconfig["ExordeApp"]["ERCAddress"]).call()
        except:
            _isNewWorkAvailable = False

        if(_isNewWorkAvailable == False): 
            if validation_printing_enabled:
                print("[Validation {}] No new work, standby.".format(dt.now()))
            return None, []
        else:
            if validation_printing_enabled:
                print("[Validation {}] New Work Available Detected.".format(dt.now()))
                print("[Validation {}] Fetching Work Batch ID".format(dt.now()))
            try:
                for trial in range(max_trials_):  
                    try:
                        gateways =  requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/ipfs_gateways.txt").text.split("\n")[:-1]
                    except:
                        time.sleep(3)
                        pass
                nb_gateways = len(gateways)
                
                
                try:
                    batchId = int(self._contract.functions.GetCurrentWork(self.app.localconfig["ExordeApp"]["ERCAddress"]).call())
                except:
                    batchId = 0
                    
                if(batchId > self._lastProcessedBatchId and batchId > self.current_batch):
                    
                    self.current_batch = batchId

                    dataBlocks = list()
                    try:
                        time.sleep(1)
                        fileList = self._contract.functions.getIPFShashesForBatch(batchId).call()
                    except:
                        fileList = []
                        
                    if validation_printing_enabled:
                        print("\t[{}]\t{}\t{}\t\t{}".format(dt.now(),"DATA BATCH VALIDATION", "Batch ID = {}".format(batchId), "PROCESSING {} batch files.".format(len(fileList))))
                    
                    for i in range(len(fileList)):
                        file = fileList[i]
                        
                        if detailed_validation_printing_enabled:
                            print("\t\tDownloading IPFS sub-file -> ",file," ... ", end='')
                        isOk = False
                        # retry all gateways twice, after pause of 10s in between, before giving up on a batch
                        for trial in range(max_trials_):    
                            _used_timeout = timeout_*(1+trial)
                            time.sleep(trial+1)
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
                                        content = None                
                                    for item in content:
                                        try:
                                            dataBlocks.append(item)
                                        except Exception as e:
                                            if detailed_validation_printing_enabled:
                                                print("\tDataBlock error", e, item)
                                            pass
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
                                time.sleep(1)
                            ## Break from trial loop if we got the file
                            if isOk:
                                break
                            time.sleep(3)
                            
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
        return False
    
    def isAdvertisingContent(self, text, debug_=False):
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
    

    def ipfs_pin_upload(self, content: str):  
        ## upload file & pin to IPFS network
        newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        endpoint_url_ = 'http://ipfs-api.exorde.network/add'
        time.sleep(0.5)
        try:
            response = requests.post(endpoint_url_, data=content ,headers=newHeaders, timeout = 60)
        except Exception as e:
            print("request pin upload error: ",e)

        response_ok = False
        json_response = None
        try:
            json_response = json.loads(response.text)
            response_ok = True
        except:
            response_ok = False
        print("[Validation]  json response = ",json_response)
        if response_ok:
            cid_obtained = json_response["cid"]
        else:
            cid_obtained = None
        return cid_obtained


    def isCommitPeriodActive(self, batchId):

        _secondsToWait = 5
        _isPeriodActive = False
        
        for i in range(5):            
            try:            
                time.sleep(4)
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
                time.sleep(4)
                _isPeriodActive = self._contract.functions.revealPeriodActive(batchId).call()
                if(_isPeriodActive == True):
                    break
            except:
                time.sleep(_secondsToWait*i)
                
        return _isPeriodActive
    
    def send_votes(self, batchId, results, status, batchResult, randomSeed):
        
        self.status = "VOTING"
        
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VOTING", "send_votes", " BatchStatus({})".format(batchResult)))
        
        
        _isUploaded = False
        _uploadTrials = 0
        
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"UPLOADING FILE", "send_votes", " BatchStatus({})".format(batchResult)))
        res = ""
        
        while(_isUploaded == False or _uploadTrials < 5):
            time.sleep(1)
            if(res == ""):
                try:                                                
                    trials_ = 0
                    while True:
                        time.sleep(2)
                        try:
                            if validation_printing_enabled:
                                print("[{}]\t{}\t{}\t\t".format(dt.now(),"FILE UPLOAD ATTEMPT ", "send_votes"))
                            _payload = json.dumps({"Content":results}, indent=4, sort_keys=True, default=str)
                            res = self.ipfs_pin_upload( _payload )
                            break

                        except Exception as e:
                            if validation_printing_enabled:
                                print("l 553 . Error: ",e)
                                print("[{}]\t{}\t{}\t\t".format(dt.now(),"FILE UPLOAD RETRY ", "send_votes"))
                            trials_ += 1
                            time.sleep(2)
                            if trials_ > 5:
                                break

                    _isUploaded = True
        
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}".format(dt.now(),"FILE UPLOADED ", "send_votes"))
                    break
                except:
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}".format(dt.now(),"FILE UPLOAD FAILED ", "send_votes"))
                    _uploadTrials += 1
                    time.sleep(5*(_uploadTrials+1))
                if(_uploadTrials >= 5):
                    break
            else:
                break
            if(_uploadTrials >= 5):
                break
            
        if validation_printing_enabled:
            print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"UPLOADING DONE", "send_votes", " BatchStatus({})".format(batchResult)))

        try:    
            if(res != "" or status != "Success"):
                if(self._contract.functions.isWorkerAllocatedToBatch(batchId, self.app.localconfig["ExordeApp"]["ERCAddress"])): #here
                
                    try:
                        time.sleep(2)
                        _didCommit = self._contract.functions.didCommit(self.app.localconfig["ExordeApp"]["ERCAddress"], batchId).call()
                    except:
                        _didCommit = False
                    
                    if detailed_validation_printing_enabled:
                        print("\t[Validation - L2] didCommit = ",_didCommit)
                
                    if(_didCommit == False):
                        
                        if detailed_validation_printing_enabled:
                            print("\t[Validation - L2] didCommit False loop => ")
                        
                        try:
                            time.sleep(2)
                            _commitPeriodOver = self._contract.functions.commitPeriodOver(batchId).call()
                        except:
                            _commitPeriodOver = False
                            
                        if detailed_validation_printing_enabled:
                            print("\t[Validation - L2] _commitPeriodOver = ",_commitPeriodOver)
                        if(_commitPeriodOver == False):
                            drop = False
                            try:
                                
                                while True:
                                    time.sleep(1)
                                    try:
                                        
                                        try:
                                            time.sleep(2)
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
                                                time.sleep(2)
                                                _commitPeriodOver = self._contract.functions.commitPeriodOver(batchId).call()
                                            except:
                                                _commitPeriodOver = False
                                                
                                            if detailed_validation_printing_enabled:
                                                print("\t[Validation - L2] _commitPeriodOver  false so wait 5s")
                                            if(_commitPeriodOver == True):
                                                drop = True
                                                break
                                    except:
                                        time.sleep(10)
                                    
                            except Exception as e:
                                pass

                            if(drop == False):
                                hasCommitted = False
                                while(hasCommitted == False):
                                    if(hasCommitted == False):
                                        try:
                                            time.sleep(2)
                                            increment_tx = self._contract.functions.commitSpotCheck(batchId, self._contract.functions.getEncryptedStringHash(res, randomSeed).call(), self._contract.functions.getEncryptedHash(batchResult, randomSeed).call(), len(results), status).buildTransaction(
                                                {
                                                    'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                                    'gasPrice': default_gas_price,
                                                    'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                                                }
                                            )
                                            self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                                            hasCommitted = True

                                            if validation_printing_enabled:
                                                print("\t[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "send_votes", "SUBMISSION & VOTE ENCRYPTED - Commited({})".format(batchId)))
                                            

                                            break
                                        except Exception as e:
                                            time.sleep(10)
                                    else:
                                        break
                                
                                while True:
                                    time.sleep(1)
                                    try:
                                        
                                        try:
                                            _revealPeriodActive = self._contract.functions.revealPeriodActive(batchId).call()
                                        except:
                                            _revealPeriodActive = False
                                            
                                        if detailed_validation_printing_enabled:
                                            print("\t[Validation - L2] _revealPeriodActive = ",_revealPeriodActive)
                                        if(_revealPeriodActive == True):
                                            break
                                        else:
                                            time.sleep(3)
                                    except:
                                        time.sleep(10)
                                    
                                
                                while True:
                                    time.sleep(1)
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
                                                        time.sleep(2)
                                                        try:
                                                            increment_tx = self._contract.functions.revealSpotCheck(batchId, res, batchResult, randomSeed).buildTransaction(
                                                                {
                                                                    'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                                                    'gasPrice': default_gas_price,
                                                                    'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                                                                }
                                                            )
                                                            self.app.tm.waitingRoom_VIP.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                                                            hasRevealed = True
                                                            
                                                            if validation_printing_enabled:
                                                                print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "send_votes", "SUBMISSION & VOTE - Revealed ({})".format(batchId)))

                                                            time.sleep(3)
                                                            self._lastProcessedBatchId = batchId
                                                            break
                                                        except Exception as e:
                                                            pass
                                                    break
                                        except Exception as e:
                                            break
                                    else:
                                        break   
                                
                                
                    else:
                        if detailed_validation_printing_enabled:
                            print("\t[Validation - L2] waiting 5s")
                        time.sleep(5)
                else:
                    print("\t[Validation - L2] Worker not allocated the batch! [Error]")

        except Exception as e:
            print(e)
            pass
    
    def process_batch(self, batchId, documents):
        
        if(batchId != None):
            
            if validation_printing_enabled:
                print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "process_batch", "PROCESSING DATA({})".format(batchId)))
        
        try:
            randomSeed = random.randint(0,999999999)
            results = list()
            ram = list()
            
            if(len(documents) > 0):
                try:
                    
                    batchResult = 1
                    for i in range(len(documents)):
                        if i%50 == 0 and detailed_validation_printing_enabled:
                                print("\t\t -> Web Content item ",int(i)," / ",len(documents))

                        try:
                            self.current_item = i                            
                            document = documents[i]
                        except:
                            document = None

                        try:    
                            response = 1
                            if(document != None):

                                document["item"]["Content"] = document["item"]["Content"].replace('"','\"')

    
                                try:
                                    debug_toggle = False
                                    if(self.isAdvertisingContent(str(document["item"]["Content"]), debug_=debug_toggle)):
                                        
                                        self._results["Advertising"] += 1
                                        response = 0


                                    if (document["item"]["Content"].strip() in ("[removed]", "[deleted]", "[citation needed]", "", "None")):
                                        self._results["Empty"] += 1
                                        response = 0
                                    
                                    if(self.isExplicitContent(document["item"]["Content"])):
                                        self._results["Censoring"] += 1
                                        response = 0
                                    
                                    if(document["item"]["Url"] in self._blacklist or document["item"]["DomainName"] in self._blacklist):
                                        self._results["Blacklist"] += 1
                                        response = 0

                                    if(self.isSpamContent(document["item"]["Author"])):
                                        self._results["Spam"] += 1
                                        response = 0

                                    if(document["item"]["Url"] in ram):
                                        self._results["Duplicates"] += 1
                                        response = 0

                                    if(response == 1):
                                        self._results["Validated"] += 1
                                        
                                        if(document["item"]["Language"] not in self._languages):
                                            self._languages[document["item"]["Language"]] = 1
                                        else:
                                            self._languages[document["item"]["Language"]] += 1
                                            
                                        # results[document["item"]] = document
                                        results.append(document)
                                        
                                        ram.append(document["item"]["Url"])                                        
                                        # ram.append(document)
                                    
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
                        print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "Processing Status:", " [{}] ".format(status)))   
                   
                    x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                    x.daemon = True
                    x.start()
                except Exception as e:
                    status = "Failure"
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "Processing Status:", " [{}] ".format(status)))   
                    batchResult = 0
                    x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                    x.daemon = True
                    x.start()
                    
            elif(len(documents) == 0):   
                status = "NoData"
                batchResult = 0
                x = threading.Thread(target=self.send_votes, args=(batchId, results, status, batchResult, randomSeed,))
                x.daemon = True
                x.start()
        except Exception as e:
            #print(e)
            pass
            
    def check_content(self, doc:str = ""):
        
            
        try:
            
            now_ts = time.time()
            delay_between_rewardsInfo = 10*60 #2 min
            try:
                if general_printing_enabled:
                    if ( now_ts -self._rewardsInfoLastTimestamp ) > delay_between_rewardsInfo or self._rewardsInfoLastTimestamp == 0: 
                        main_addr = self.app.localconfig["ExordeApp"]["MainERCAddress"]       
                        time.sleep(0.5) 
                        to = 10
                        # mainnet_config_github_url = 'https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/NetworkConfig.txt'
                        # testnet_config_github_url = 'https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt'
                        # mainnet_contracts = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ContractsAddresses.txt", timeout=to).json()
                        # testnet_contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()

                        # netConfig_mainnet = requests.get(mainnet_config_github_url, timeout=30).json()
                        # netConfig_testnet = requests.get(testnet_config_github_url, timeout=30).json()

                        # w3_mainnet = Web3(Web3.HTTPProvider(netConfig_mainnet["_urlSkale"]))
                        # w3_testnet = Web3(Web3.HTTPProvider(netConfig_testnet[sync_node_id]))

                        # abi_rep = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/Reputation.sol/Reputation.json", timeout=to).json()

                        # base_rep_archive_url_ = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/archives/partial_testnets/base_reputation_amount.json"
                        base_rep_archive_url_ = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"

                        base_rep_archive_ = requests.get(base_rep_archive_url_, timeout=to).json()
                        rep_amount_base_archive = 0
                        if main_addr in base_rep_archive_:
                            rep_amount_base_archive = base_rep_archive_[main_addr]

                        # contract_mainnet = w3_mainnet.eth.contract(mainnet_contracts["Reputation"], abi=abi_rep["abi"])
                        # contract_testnet = w3_testnet.eth.contract(testnet_contracts["Reputation"], abi=abi_rep["abi"])

                        # rep_amount_mainnet = round(contract_mainnet.functions.balanceOf(main_addr).call()/(10**18),4)
                        # rep_amount_testnet = round(contract_testnet.functions.balanceOf(main_addr).call()/(10**18),4)

                        # rep_amount = round(rep_amount_testnet + rep_amount_mainnet + rep_amount_base_archive,4)
                        # rep_amount = round(rep_amount_testnet + rep_amount_base_archive,4)
                        rep_amount = round(rep_amount_base_archive,4)


                        # rep_amount = round(self.app.cm.instantiateContract("Reputation").functions.balanceOf(main_addr).call()/(10**18),2)
                        print("[CURRENT REWARDS & REP] Main Address {}, REP Rewards = {}, Time of snapshot = {} (Source: Testnet Leaderboard)".format(str(main_addr), rep_amount, dt.now()))
                        self._rewardsInfoLastTimestamp = now_ts
            except Exception as e:
                print(e)
                time.sleep(2)
                pass
            
            try:
                batchId, documents = self.get_content()
            except Exception as e:
                if detailed_validation_printing_enabled:
                    print("Error 949 get_content: ",e)
            
            if(batchId != None):
                
                if(batchId != None and batchId >= self.current_batch):
                    if validation_printing_enabled:
                        print("[{}]\t{}\t{}\t\t{}".format(dt.now(),"VALIDATION", "check_content", "PROCESSING({})".format(batchId)))
                    try:
                        self.totalNbBatch += 1
                        self.batchLength = len(documents)
                        
                        self._lastProcessedBatchId = batchId
                        self.process_batch(batchId, documents)
                        self._isRunning = False
                    except Exception as e:
                        if detailed_validation_printing_enabled:
                            print("Error 965: ",e)
                        self._isRunning = False
                else:
                    self.status = "OLDJOB"
            else:
                self.status = "NOJOB"
                
        except Exception as e:
            self._isRunning = False