# -*- coding: utf-8 -*-
"""
Created on 09 01 2023

@author: florent, mathias
Exorde Labs
"""


from web3.middleware import simple_cache_middleware
try:
    w3.middleware_onion.add(simple_cache_middleware)
except Exception as e:
    print("w3 middleware error: ",e)

default_gas_amount = 1_200_000
gas_cap_min = 1_200_000

default_gas_price = 100_000 # 100000 wei or 0.0001

class ContractManager():
    
    def __init__(self, address = "", key =""):
        if detailed_validation_printing_enabled:
            print("[ContractManager] Init...")

        self._AccountAddress = address
        self._AccountKey = key
        # w3 = Web3(Web3.HTTPProvider(self.netConfig["_urlSkale"]))


        if mainnet_selected:
            self.netConfig = requests.get(mainnet_config_github_url, timeout=30).json()
        else:    
            self.netConfig = requests.get(testnet_config_github_url, timeout=30).json()
        
        to = 5
        
        if mainnet_selected:
            self.contracts = requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ContractsAddresses.txt", timeout=to).json()
        else:
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
        self.abis["StakingManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/StakingManager.sol/StakingManager.json", timeout=to).json()
        self.abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
        self.abis["AddressManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/AddressManager.sol/AddressManager.json", timeout=to).json()


        if detailed_validation_printing_enabled:
            print("[ContractManager] Initialized")

    def instantiateContract(self, arg: str):
        
        contract = w3.eth.contract(self.contracts[arg], abi=self.abis[arg]["abi"])
        return contract
    
    def readStake(self):
        
        sm = self.instantiateContract("StakingManager")
        time.sleep(0.5)
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        if(stakeAmount > Web3.toWei(25, 'ether')):
            return True
        else:
            return False
        
    def StakeManagement(self, transactManager):
        
        contract = self.instantiateContract("EXDT")
        sm = self.instantiateContract("StakingManager")
        
        time.sleep(0.5)
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        time.sleep(0.5)
        stakeAllocated = sm.functions.AllocatedStakedAmountOf(self._AccountAddress).call()
        
        if(stakeAmount >= 100 ):
            return True
        else:

            try:
                cur_nounce_ = w3.eth.get_transaction_count(self._AccountAddress)
                amount = Web3.toWei(100, 'ether')
                increment_tx = contract.functions.approve(self.contracts["StakingManager"], amount).buildTransaction(
                    {
                        'from': self._AccountAddress,
                        'gasPrice': default_gas_price,
                        'nonce': cur_nounce_,
                    }
                )
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
                
                time.sleep(0.5)
                amount_check = contract.functions.allowance(self._AccountAddress, self.contracts["StakingManager"]).call()

                
                increment_tx = sm.functions.deposit(Web3.toWei(100, 'ether')).buildTransaction(
                   {
                       'from': self._AccountAddress,
                       'gasPrice': default_gas_price,
                       'nonce': cur_nounce_,
                   }
               )
                
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
               
                increment_tx = sm.functions.Stake(Web3.toWei(100, 'ether')).buildTransaction(
                   {
                       'from': self._AccountAddress,
                       'gasPrice': default_gas_price,
                       'nonce': cur_nounce_,
                   }
               )
                transactManager.waitingRoom.put((increment_tx, self._AccountAddress, self._AccountKey))
                time.sleep(30)
            except Exception as e:
                pass
            return True


    
class TransactionManager():    
    def __init__(self, cm):        
        
        if detailed_validation_printing_enabled:
            print("[TransactionManager] Init....")

        self.netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt", timeout=20).json()
        # w3 = Web3(Web3.HTTPProvider(self.netConfig["_urlSkale"]))
        # w3Tx = Web3(Web3.HTTPProvider(self.netConfig["_urlTxSkale"]))
        self.waitingRoom = Queue()
        self.waitingRoom_VIP = Queue()
        self.usedGasCache = dict()
        self.run = True
        # try:
        #     self.last_block = w3.eth.get_block('latest')["number"]-1
        # except:
        #     self.last_block = 0
        self.cm = cm
        x = threading.Thread(target=self.SendTransactions)        
        x.daemon = True
        x.start()
        if detailed_validation_printing_enabled:
            print("[TransactionManager] Initialiazed.")



        
    def SendTransactions(self):
        
        while True:
            if(self.waitingRoom_VIP.qsize() == 0 and self.waitingRoom.qsize() == 0):
                time.sleep(3)
                pass
            else:
                time.sleep(1) # sleep anyway, be nice with the network
                try:
                    if(self.waitingRoom_VIP.qsize() != 0):
                        for k_sending_trials in range(2):
                            try:
                                time.sleep(1+k_sending_trials*3.5)
                                increment_tx = self.waitingRoom_VIP.get()                                 
                                previous_nounce = w3.eth.get_transaction_count(increment_tx[1])

                                increment_tx[0]["nonce"] = previous_nounce
                                
                                ####### caching system
                                # get the first 4 bytes of the function being called, in the data
                                function_bytecode = str(increment_tx[0]["data"])[2:10]
                                data_length = len(str(increment_tx[0]["data"]))
                                if detailed_validation_printing_enabled:
                                    print("DATA LENGTH = ",data_length," & function bytecode = ",function_bytecode)
                                gas_key_ = (function_bytecode, data_length)

                                # NOT IN CACHE YET:
                                if gas_key_ not in self.usedGasCache:

                                    gas = default_gas_amount
                                    try:
                                        gasEstimate = w3.eth.estimate_gas(increment_tx[0])*1.5
                                        if gasEstimate < 100_000:
                                            gas = gasEstimate + 500_000
                                        gas = max(gas_cap_min, gas)
                                        ### add to cache
                                        self.usedGasCache[gas_key_] = gas
                                    except  Exception as e:
                                        if detailed_validation_printing_enabled:
                                            print("[TRANSACTION MANAGER] Gas estimation failed: ",e)
                                # IN CACHE :
                                else:
                                    cached_used_gas = self.usedGasCache[gas_key_]
                                    gas = max(gas_cap_min, cached_used_gas)

                                increment_tx[0]["gas"] = int(round(int(gas),0))
                                increment_tx[0]["gasPrice"] = int(default_gas_price)

                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)

                                # SIGN TRANSACTION
                                tx_create = w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])

                                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                                
                                try:
                                    tx_hash = w3Tx.eth.send_raw_transaction(tx_create.rawTransaction)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION RAW SEND ERROR]: ",e)
                                        break
                                
                                time.sleep(2)
                                for i in range (10):
                                    time.sleep(i*1.5+1)
                                    # WAIT FOR NEW NOUNCE BY READING PROXY
                                    current_nounce = w3.eth.get_transaction_count(increment_tx[1])
                                    if(current_nounce > previous_nounce):
                                        # found a new transaction because account nounce has increased
                                        break

                                # WAIT FOR TX RECEIPT
                                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                                try:       
                                    tx_gasUsed = tx_receipt['gasUsed']
                                    tx_status = int(tx_receipt['status'])
                                    tx_status_str = "Failure"
                                    if tx_status == 1 :
                                        tx_status_str = "Success"
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Transaction Status = ", tx_status_str, " , Gas used = ",tx_gasUsed)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Tx Receipt failed : ",e)

            
                                break
                            except Exception as e:
                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Error : ",e)
                                pass
                    
                    else:
                        for k_sending_trials in range(2):
                            try:
                                time.sleep(1+k_sending_trials*3.5)
                                increment_tx = self.waitingRoom.get() 
                                    
                                previous_nounce = w3.eth.get_transaction_count(increment_tx[1])

                                increment_tx[0]["nonce"] = previous_nounce
                                ####### caching system
                                # get the first 4 bytes of the function being called, in the data
                                function_bytecode = str(increment_tx[0]["data"])[2:10]
                                data_length = len(str(increment_tx[0]["data"]))
                                if detailed_validation_printing_enabled:
                                    print("DATA LENGTH = ",data_length," & function bytecode = ",function_bytecode)
                                gas_key_ = (function_bytecode, data_length)

                                # NOT IN CACHE YET:
                                if gas_key_ not in self.usedGasCache:
                                    if detailed_validation_printing_enabled:
                                        print("---------------------------    NOT CACHED GAS: estimating... ")

                                    gas = default_gas_amount
                                    try:
                                        gasEstimate = w3.eth.estimate_gas(increment_tx[0])*1.5
                                        if gasEstimate < 100_000:
                                            gas = gasEstimate + 500_000
                                        gas = max(gas_cap_min, gas)
                                        ### add to cache
                                        self.usedGasCache[gas_key_] = gas
                                    except  Exception as e:
                                        if detailed_validation_printing_enabled:
                                            print("[TRANSACTION MANAGER] Gas estimation failed: ",e)
                                # IN CACHE :
                                else:
                                    cached_used_gas = self.usedGasCache[gas_key_]
                                    gas = max(gas_cap_min, cached_used_gas)
                                    if detailed_validation_printing_enabled:
                                        print("---------------------------    CACHED GAS: ",cached_used_gas)

                                increment_tx[0]["gas"] = int(round(int(gas),0))
                                increment_tx[0]["gasPrice"] = int(default_gas_price)
                                                
                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)

                                # SIGN TRANSACTION
                                tx_create = w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])

                                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                                try:
                                    tx_hash = w3Tx.eth.send_raw_transaction(tx_create.rawTransaction)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION RAW SEND ERROR]: ",e)
                                        break
                                
                                time.sleep(2)
                                for i in range (10):
                                    time.sleep(i*1.5+1)
                                    # WAIT FOR NEW NOUNCE BY READING PROXY
                                    current_nounce = w3.eth.get_transaction_count(increment_tx[1])
                                    if(current_nounce > previous_nounce):
                                        # found a new transaction because account nounce has increased
                                        break

                                # WAIT FOR TX RECEIPT
                                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                                try:       
                                    tx_gasUsed = tx_receipt['gasUsed']
                                    tx_status = int(tx_receipt['status'])
                                    tx_status_str = "Failure"
                                    if tx_status == 1 :
                                        tx_status_str = "Success"
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Transaction Status = ", tx_status_str, " , Gas used = ",tx_gasUsed)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Tx Receipt failed : ",e)

                                # self.last_block = w3.eth.get_block('latest')["number"]
                                break
                            except Exception as e:
                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Error : ",e)
                                pass
                except Exception as e:
                    if detailed_validation_printing_enabled:
                        print("[TRANSACTION MANAGER] Major Error : ",e)
                    time.sleep(3)
                    pass
                    
                    
#print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"TRANSACTION", "import", "LOADED"))                    