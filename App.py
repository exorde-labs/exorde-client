# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 14:20:53 2022

@author: florent, mathias
Exorde Labs
"""


class Widget():
    
    def __init__(self):        
        
        try:
            locInfo = requests.get("http://ipinfo.io/json").json()
            self.userCountry = Web3.toHex(text=json.dumps(locInfo)) #["country"]
        except:
            self.userCountry = Web3.toHex(text="Unknown")
        
        netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
        self.w3 = Web3(Web3.HTTPProvider(netConfig["_urlSkale"]))        
        self.w3Tx = Web3(Web3.HTTPProvider(netConfig["_urlTxSkale"]))

        
        if general_printing_enabled:
            print("\n[Init] UPDATING CONFIG")
        self.readLocalConfig()

        
        x = threading.Thread(target=self.submarineManagement)
        x.daemon = True
        x.start()

        contracts = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ContractsAddresses.txt", timeout=to).json()
        abis = dict()
        abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()

        config_reg_contract = self.w3.eth.contract(contracts["ConfigRegistry"], abi=abis["ConfigRegistry"]["abi"])

        # Check Updates                
        with open("localConfig.json", "r") as f:
            localconfig = json.load(f)
        
        ## check update   
        try:
            if general_printing_enabled:
                print("[Init Version Check] Checking version on start")    
            try:
                _version = config_reg_contract.functions.get("version").call()
                _lastInfo = config_reg_contract.functions.get("lastInfo").call()
                print("Latest message from Exorde Labs: ",_lastInfo)
            except:
                _version = localconfig["ExordeApp"]["lastUpdate"]
            
            if("lastUpdate" not in localconfig["ExordeApp"]):            
                localconfig["ExordeApp"]["lastUpdate"] = _version
                with open("localConfig.json", "w") as f:
                    json.dump(localconfig, f)
                    
            if(localconfig["ExordeApp"]["lastUpdate"] != _version):          
                print("[Init Version Check] Updated to Version: ",_version)
                localconfig["ExordeApp"]["lastUpdate"] = _version
                with open("localConfig.json", "w") as f:
                    json.dump(localconfig, f)
            else:                
                print("[Init Version Check] Current Module Version: ",_version)
        except Exception as e:
            print("[Init Version Check] Error: ",e)

        nb_trials_reading_config = 0
        nb_max_before_interrup = 4
        while True:
                
            time.sleep(5*60)
            ## Check RemoteKill   
            try:
                try:
                    _remote_kill = str(config_reg_contract.functions.get("remote_kill").call())
                except:
                    nb_trials_reading_config += 1
                    time.sleep(2)
                
                if(_remote_kill == "kill"):
                    print("Forced Interruption of your Exorde Module. Check Discord for any update")  
                    exit(1)
                                    
                if(nb_trials_reading_config >= nb_max_before_interrup ):        
                    print("Could not read ConfigRegistry ",nb_max_before_interrup," times in a row. The Network might be in trouble, check Discord for any update.")  
                    exit(1)
            except Exception as e:
                print("RemoteKill Error = ",e)




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
        
        max_nb_autofaucet_trials = 10
        nb_autofaucet_trials = 0
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
                
                previous_nounce = self.w3.eth.get_transaction_count(faucet_address)

                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                tx_hash = self.w3Tx.eth.send_raw_transaction(signed_txn.rawTransaction)

                time.sleep(2)
                for i in range (10):
                    time.sleep(i*1.5+1)
                    # WAIT FOR NEW NOUNCE BY READING PROXY
                    current_nounce = self.w3.eth.get_transaction_count(faucet_address)
                    if(current_nounce > previous_nounce):
                        # found a new transaction because account nounce has increased
                        break

                # WAIT FOR TX RECEIPT
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                
                    
                print("[Faucet] sfuel funding tx = ",tx_receipt.transactionHash.hex())
                
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
                previous_nounce = self.w3.eth.get_transaction_count(faucet_address)

                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                tx_hash = self.w3Tx.eth.send_raw_transaction(signed_txn.rawTransaction)

                time.sleep(2)
                for i in range (10):
                    time.sleep(i*1.5+1)
                    # WAIT FOR NEW NOUNCE BY READING PROXY
                    current_nounce = self.w3.eth.get_transaction_count(faucet_address)
                    if(current_nounce > previous_nounce):
                        # found a new transaction because account nounce has increased
                        break

                # WAIT FOR TX RECEIPT
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                
                
                print("[Faucet] token funding tx = ",tx_receipt.transactionHash.hex())

                time.sleep(1)
                _trials = 5
                read_status = False
                for i in range(_trials):
                    try:                             
                        token_balance = tok_contract.functions.balanceOf(user_address).call()
                        user_token_balance = self.w3.fromWei(token_balance, 'ether')
                        user_sfuel_balance = self.w3.eth.get_balance(user_address)
                        read_status = True
                        break
                    except Exception as e:
                        time.sleep((1+int(i)))
                
                if read_status == False:
                    continue

                print('[Faucet] Worker EXDT Balance:', user_token_balance, " ")
                print('[Faucet] Worker sFuel Balance:', user_sfuel_balance, " sFUEL")

                if user_token_balance > 0 and user_sfuel_balance > 0:
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
    try:
        wdg = Widget()
    except Exception as e:
        print("Init error",e)        

