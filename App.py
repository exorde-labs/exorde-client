# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 14:20:53 2022

@author: florent, mathias
Exorde Labs
"""
# from datetime import datetime
import time

default_gas_price = 100_000 # 100000 wei or 0.0001

class Widget():
    def __init__(self):        
        

        if validation_printing_enabled:
            print("[App] sub routine initialized")

        try:
            locInfo = requests.get("http://ipinfo.io/json",timeout=30).json()
            self.userCountry = locInfo["country"]
        except:
            self.userCountry = Web3.toHex(text="Unknown")
        

        abis = dict()
        abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
        abis["DataSpotting"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/DataSpotting.sol/DataSpotting.json", timeout=to).json()

        # w3 = Web3(Web3.HTTPProvider(netConfig["_urlSkale"]))        
        # w3Tx = Web3(Web3.HTTPProvider(netConfig["_urlTxSkale"]))

        config_reg_contract = w3.eth.contract(contracts["ConfigRegistry"], abi=abis["ConfigRegistry"]["abi"])
        spot_worksystem_contract = w3.eth.contract(contracts["DataSpotting"], abi=abis["DataSpotting"]["abi"])

        # Check Updates                
        with open("localConfig.json", "r") as f:
            localconfig = json.load(f)
    

        try:
            _remote_kill = ""
            try:
                time.sleep(1)
                _remote_kill = str(config_reg_contract.functions.get("remote_kill").call())               
                time.sleep(1)
                _amIKicked = spot_worksystem_contract.functions.AmIKicked().call()
                
                print("[Initial Worker Check] KICK STATUS: ",_amIKicked)
                if _amIKicked:
                    print("\n*******\nYou are kicked for inactivity, you might be running too many workers for your machine / internet connection. Waiting 3 hours.\n",
                    "Restarting will not help, please don't spam the network, Exorde has to regulate itself\n*******")
                    time.sleep(3600*3) # wait 3 hours
                    exit()
            except Exception as e:
                print("Failed to read remote_kill & kick status: ",e)
                time.sleep(2)

            if(_remote_kill == "kill"):
                print("Forced Interruption of your Exorde Module. Check Discord for any update")         
                curr_dt = dt.now()
                _timestamp_now = int(round(curr_dt.timestamp()))

                if("lastTimestamp" not in localconfig["ExordeApp"]):            
                    localconfig["ExordeApp"]["lastTimestamp"] = _timestamp_now
                    with open("localConfig.json", "w") as f:
                        json.dump(localconfig, f)

                if("lastTimestamp" in localconfig["ExordeApp"]):
                    last_ts_ = localconfig["ExordeApp"]["lastTimestamp"]
                    wait_duration = 30*60
                    if last_ts_ >= ( _timestamp_now - wait_duration ): # wait 30 min
                        print("[ Safety Sleep ] Waiting until close, let's reduce repetitive restarts ...")
                        time.sleep(wait_duration)
                    localconfig["ExordeApp"]["lastTimestamp"] = _timestamp_now
                    with open("localConfig.json", "w") as f:
                        json.dump(localconfig, f)
                    exit()



                exit(1)
        except Exception as e:
            print("App error: ",e)
                
        try:
            self.readLocalConfig()
        except Exception as e:
            print("Error reading local config: ",e,"\n")

        
        x1 = threading.Thread(target=self.submarineManagement)
        x1.daemon = True
        x1.start()

        ## check update   
        try:
            if general_printing_enabled:
                print("\n[Init Version Check] Checking version on start")    
            try:
                time.sleep(1)
                _version = config_reg_contract.functions.get("version").call()
                time.sleep(1)
                _lastInfo = config_reg_contract.functions.get("lastInfo").call()
                print("Latest message from Exorde Labs: ",_lastInfo)
            except Exception as e:
                print("[Init Version Check 1] Error: ",e)
                _version = localconfig["ExordeApp"]["lastUpdate"]
                _lastInfo = localconfig["ExordeApp"]["lastInfo"]
                
            
            if("lastUpdate" not in localconfig["ExordeApp"]):         
                with open("localConfig.json", "w") as f:
                    json.dump(localconfig, f)
                    
            if(localconfig["ExordeApp"]["lastUpdate"] != _version or localconfig["ExordeApp"]["lastInfo"] != _lastInfo):  
                localconfig["ExordeApp"]["lastInfo"] = _lastInfo           
                localconfig["ExordeApp"]["lastUpdate"] = _version
                print("[Init Version Check] Updated to Version: ",_version)
                with open("localConfig.json", "w") as f:
                    json.dump(localconfig, f)
            else:                
                print("[Init Version Check] Current Module Version: ",_version)
        except Exception as e:
            print("[Init Version Check 2] Error: ",e)

        nb_trials_reading_config = 0
        nb_max_before_interrup = 4
        last_trial_timestamp = int(round((dt.now()).timestamp()))
        max_acceptable_nocheck_duration = 120*60
        while True:                
            ## Check RemoteKill   
            for i in range(nb_max_before_interrup):
                try:
                    _remote_kill = ""
                    try:
                        time.sleep(i*3+1)
                        _remote_kill = str(config_reg_contract.functions.get("remote_kill").call())                        
                        last_trial_timestamp = int(round((dt.now()).timestamp()))
                        break
                    except Exception as e:
                        if detailed_validation_printing_enabled:
                            print("Failed to read config :",e)
                        nb_trials_reading_config += 1
                        time.sleep(30)
                except Exception as e:
                    print("RemoteKill Error = ",e)
            
            if(_remote_kill == "kill"):
                print("Forced Interruption of your Exorde Module. Check Discord for any update")  
                exit(1)

            now_ts = int(round((dt.now()).timestamp()))          
            
            if last_trial_timestamp < ( now_ts - max_acceptable_nocheck_duration ): # wait 30 min max    
                print("[Remote Kill Status Check] Could not read ConfigRegistry ",nb_max_before_interrup," times in a row, in a period of 30min. The Network might be in trouble, please wait.")  
                exit(1) 

            time.sleep(5*60)
            

    if validation_printing_enabled:
        print("[App Core] Initialized")




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
        #print("[{}]\t{}\t{}\t\t{}".format(dt.dt.now(),"WIDGET", "submarineManagement", self.status))
        self.createUtils()
        # self.stakeChecking()
        
        print("**********************[Init] dbg0")
        self.am = self.cm.instantiateContract("AddressManager")
        cur_nounce = w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"])

        if detailed_validation_printing_enabled:
            print("[stakeChecking] Debug nounce = ",cur_nounce)

        if validation_printing_enabled:
            print("[Init Worker Master] Claiming Master")

        print("**********************[Init] dbg1")
        increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
            {
                'from': self.localconfig["ExordeApp"]["ERCAddress"],
                'gasPrice': default_gas_price,
                'nonce': cur_nounce,
            }
        )
        print("**********************[Init] dbg2")
        self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))
        print("**********************[Init] dbg3")
        
        if general_printing_enabled:
            print("[Init] CREATING DATA COLLECTION SUBROUTINE")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.dt.now(),"WIDGET", "submarineManagement", self.status))
        self.sm = Scraper(self)
        
        print("**********************[Init] dbg4")
        self.spotThread = threading.Thread(target=self.sm.manage_scraping)        
        self.spotThread.daemon = True
        self.spotThread.start()
        
        if general_printing_enabled:
            print("[Init] CREATING VALIDATION SUBROUTINE")
        #print("[{}]\t{}\t{}\t\t{}".format(dt.dt.now(),"WIDGET", "submarineManagement", self.status))
        
        self.val = Validator(self)
        # self.checkThread = threading.Thread(target=self.val.manage_checking)
        # self.checkThread.start()
        
        
    def to_explorer(self):
        
        x2 = threading.Thread(target=webbrowser.open_new, args=("http://explorer.exorde.network/",))
        x2.daemon = True
        x2.start()
        #webbrowser.open_new("http://explorer.exorde.network/")
        
    def openFormattingScreen(self):
        
        x3 = threading.Thread(target=webbrowser.open_new, args=("https://light-vast-diphda.explorer.mainnet.skalenodes.com/address/{}/transactions".format(self.localconfig["ExordeApp"]["ERCAddress"]),))
        x3.daemon = True
        x3.start()
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
        
        ### DECODE PRIVATE KEY FOR STORAGE
        
        user_address = self.localconfig["ExordeApp"]["ERCAddress"]

        ##### 0 - CHECK VALIDITY                
        is_user_address_valid = w3.isAddress(user_address)
        if is_user_address_valid == False:
            print("[Init] INVALID USER ADDRESS, ABORT")
            os._exit(1)
        user_address = w3.toChecksumAddress(user_address)
        
        time.sleep(1)

        for i in range (3):
            time.sleep(i*1.5+1)
            try:
                self_balance = int(w3.eth.get_balance(user_address))
                break
            except:
                self_balance = 0

        print("[Pre-Faucet check] User sFuel Balance = ",round(self_balance/(10**18),4))

        if self_balance == 0:
            if general_printing_enabled:
                print("[Initial Auto Faucet] Top up sFuel & some EXDT to worker address...")
            EXDT_token_address = "0xcBc357F3077989B4636E93a8Ce193E05cd8cc56E"

            faucet_success = False
                    
            faucet_delay = randint(5,1*60) # sleep randomly between 30s & 10 minutes
            print("[ Faucet ] Waiting ",faucet_delay, " seconds before trying")
            time.sleep(faucet_delay)

            max_nb_autofaucet_trials = 3
            nb_autofaucet_trials = 0
            while faucet_success == False:
                try:                
                    time.sleep(5)
                    # select random faucet out of the  500 ones
                    (fi, Private_key) = self.select_random_faucet_pk()
                    if general_printing_enabled:
                        print("[Faucet] selecting Auto-Faucet n°",fi)
                    faucet_address = w3.eth.account.from_key(Private_key).address

                    # faucet_balance = w3.eth.get_balance(faucet_address)/(10**18)
                    # print("[Faucet] Selected faucet balance = ",faucet_balance," sFuel")
                    # if faucet_balance <= 0:
                    #     continue
                    
                    previous_nounce = w3.eth.get_transaction_count(faucet_address)

                                
                    ### 1 - SEND FUEL FIRST
                    #print("SEND FUEL")
                    signed_txn = w3.eth.account.sign_transaction(dict(
                        nonce=previous_nounce,
                        gasPrice=default_gas_price,
                        gas=100_000,
                        to=user_address,
                        value=500000000000000,
                        data=b'Hi Exorde!',
                    ),
                    Private_key,
                    )
                    
                    # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                    tx_hash = w3Tx.eth.send_raw_transaction(signed_txn.rawTransaction)

                    time.sleep(3)
                    for i in range (10):
                        time.sleep(i*1.5+1)
                        # WAIT FOR NEW NOUNCE BY READING PROXY
                        current_nounce = w3.eth.get_transaction_count(faucet_address)
                        if(current_nounce > previous_nounce):
                            # found a new transaction because account nounce has increased
                            break

                    # WAIT FOR TX RECEIPT
                    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                    
                        
                    print("[Faucet] sfuel funding tx = ",tx_receipt.transactionHash.hex())
                    
                    token_abi = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/daostack/controller/daostack/controller/DAOToken.sol/DAOToken.json"
                    ,timeout=10).json()["abi"]
                    tok_contract = w3.eth.contract(EXDT_token_address, abi=token_abi)
                        
                    ### 1 - SEND EXDT TOKENS          
                    if False:          # disabled
                        token_amount_to_send = 200000000000000000000 # 200 tokens EXDT
                        increment_tx = tok_contract.functions.transfer(user_address, token_amount_to_send).buildTransaction({
                                'from': faucet_address,
                                'nonce': w3.eth.get_transaction_count(faucet_address),
                                'value': 0,
                                'gas': 1000000,
                                'gasPrice': default_gas_price,
                        })
                        
                        tx_create = w3.eth.account.sign_transaction(increment_tx, Private_key)
                        previous_nounce = w3.eth.get_transaction_count(faucet_address)

                        # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                        tx_hash = w3Tx.eth.send_raw_transaction(signed_txn.rawTransaction)

                        time.sleep(2)
                        for i in range (10):
                            time.sleep(i*1.5+1)
                            # WAIT FOR NEW NOUNCE BY READING PROXY
                            current_nounce = w3.eth.get_transaction_count(faucet_address)
                            if(current_nounce > previous_nounce):
                                # found a new transaction because account nounce has increased
                                break

                        # WAIT FOR TX RECEIPT
                        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                        
                        
                        print("[Faucet] token funding tx = ",tx_receipt.transactionHash.hex())

                    time.sleep(1)
                    _trials = 3
                    read_status = False
                    for i in range(_trials):
                        try:                 
                            time.sleep(2)            
                            # token_balance = tok_contract.functions.balanceOf(user_address).call()
                            # user_token_balance = w3.fromWei(token_balance, 'ether')
                            user_sfuel_balance = w3.eth.get_balance(user_address)
                            read_status = True
                            break
                        except Exception as e:
                            time.sleep((1+int(i)))
                    
                    if read_status == False:
                        print("[Faucet] Could not read balance")
                        continue

                    # print('[Faucet] Worker EXDT Balance:', user_token_balance, " ")
                    print('[Faucet] Worker sFuel Balance:', user_sfuel_balance, " sFUEL")

                    if  user_sfuel_balance > 0:
                        faucet_success = True
                        print("[Faucet] Auto-Faucet n°",fi, " Success.")
                        break
                    nb_autofaucet_trials += 1
                    if nb_autofaucet_trials >= max_nb_autofaucet_trials:
                        print("[Faucet] Auto-Faucet Failure. Tried ",max_nb_autofaucet_trials," times. Giving up. Please report this error. Faucets might be empty.")
                        exit(1)
                except Exception as e:
                    print("[Faucet] Error: ",e)
                    print("[Faucet] Auto-Faucet n°",fi, " Failure... retrying.")
                    nb_autofaucet_trials += 1
                    time.sleep(1+(nb_autofaucet_trials)*2)
                    if nb_autofaucet_trials >= max_nb_autofaucet_trials:
                        print("[Faucet] Auto-Faucet critical Failure. Tried ",max_nb_autofaucet_trials," times. Giving up. Please report this error.")
                        exit(1)
                    continue
        else:
            print("No need to faucet.")
        
    def createUtils(self):        
        if detailed_validation_printing_enabled:
            print("[Debug] createUtils: self.cm = ContractManager()")
        self.cm = ContractManager(self.localconfig["ExordeApp"]["ERCAddress"], self.pKey)
        time.sleep(1)
        if detailed_validation_printing_enabled:
            print("[Debug] createUtils: self.tm = TransactionManager(self.cm)")
        self.tm = TransactionManager(self.cm)
        
            
    def generateLocalKey(self):
        random.seed(random.random())
        baseSeed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=256))
        acct = Account.create(baseSeed)
        key = acct.key
        return acct.address, key
    
    def stakeChecking(self):
        
        #print("[{}]\t{}\t{}\t\t{}".format(dt.dt.now(),"WIDGET", "stakeChecking", self.status))

        if validation_printing_enabled:
            print("[stakeChecking] Instanciating AddressManager")

        self.am = self.cm.instantiateContract("AddressManager")
        cur_nounce = w3.eth.get_transaction_count(self.localconfig["ExordeApp"]["ERCAddress"])

        if detailed_validation_printing_enabled:
            print("[stakeChecking]debug nounce = ",cur_nounce)

        if self.localconfig["ExordeApp"]["MainERCAddress"] != "":
                
            if validation_printing_enabled:
                print("[Init Worker Master] Claiming Master")

            increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                {
                    'from': self.localconfig["ExordeApp"]["ERCAddress"],
                    'gasPrice': default_gas_price,
                    'nonce': cur_nounce,
                }
            )
            self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))

        if(self.cm.readStake() == True):

            self.am = self.cm.instantiateContract("AddressManager")

            if(self.localconfig["ExordeApp"]["MainERCAddress"] != ""):

                if validation_printing_enabled:
                    print("[Init Worker Master] Claiming Master")
                    
                increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                    {
                        'from': self.localconfig["ExordeApp"]["ERCAddress"],
                        'gasPrice': default_gas_price,
                        'nonce': cur_nounce,
                    }
                )
                self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))
        else:
            
            requests.post("https://api.faucet.exorde.network/fundAccount/"+self.localconfig["ExordeApp"]["ERCAddress"])
            
            self.am = self.cm.instantiateContract("AddressManager")

            if(self.localconfig["ExordeApp"]["MainERCAddress"] != ""):

                if validation_printing_enabled:
                    print("[Init Worker Master] Claiming Master")
                increment_tx = self.am.functions.ClaimMaster(self.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                    {
                        'from': self.localconfig["ExordeApp"]["ERCAddress"],
                        'gasPrice': default_gas_price,
                        'nonce': cur_nounce,
                    }
                )
                self.tm.waitingRoom_VIP.put((increment_tx, self.localconfig["ExordeApp"]["ERCAddress"], self.pKey))

        # self.cm.StakeManagement(self.tm)  ###DISABLED STAKING FOR TESTNET -> too many txs, no purpose
        if general_printing_enabled:
            print("[Init]  EXDT Staking requirement OK ")
        


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
                print("[Init] First funding of the worker wallet")
            
            with open('bob.txt', "wb") as file:
                file.write(self.pKey)
                
            self.localconfig = new_conf    

        else:
            with open('bob.txt', "rb") as file:
                self.pKey = file.read()
        
        # updating localconfig with new MainERCAddress
        with open("localConfig.json", "w") as f:
            json.dump(new_conf,f)

        # Autofund anyway, in case worker balance is zero
        try:
            self.autofund()
        except Exception as e:
            print("Autofund check failed: ",e)
        
                        
        try:
            self.allowGeoCoordSending = self.localconfig["ExordeApp"]["SendCountryInfo"]
        except:
            self.allowGeoCoordSending = 1
                 

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

        
        
    def on_closing(self, master):
        if general_printing_enabled:
            print("[ClaimMaster] Claiming...")
        
        new_val = main_wallet_
        if(new_val == ""):
            print("No Main Ethereum Wallet", "Please indicate your main Ethereum wallet address.")
        else:
            master.localconfig["ExordeApp"]["MainERCAddress"] = new_val
            with open('bob.txt', "rb") as file:
                pKey = file.read()
            am = master.cm.instantiateContract("AddressManager")
            time.sleep(1)
            increment_tx = am.functions.ClaimMaster(master.localconfig["ExordeApp"]["MainERCAddress"]).buildTransaction(
                {
                    'from': master.localconfig["ExordeApp"]["ERCAddress"],
                    'gasPrice': master.default_gas_price,
                    'nonce': master.w3.eth.get_transaction_count(master.localconfig["ExordeApp"]["ERCAddress"]),
                }
            )
            master.tm.waitingRoom_VIP.put((increment_tx, master.localconfig["ExordeApp"]["ERCAddress"], master.pKey, True))
            
            master.updateLocalConfig()
            self.user_info.destroy()

            
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
            pass

        
def desktop_app():
    for globaltrial in range(3):
        try:
            wdg = Widget()
        except Exception as e:
            print("Init error",e)
            print("Retrying in 60s...")
            time.sleep(60)
            print("Retrying.")