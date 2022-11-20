# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 14:20:53 2022

@author: florent, mathias
Exorde Labs
"""


default_gas_amount = 10_000_000

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
        self.abis["StakingManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/StakingManager.sol/StakingManager.json", timeout=to).json()
        self.abis["ConfigRegistry"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/ConfigRegistry.sol/ConfigRegistry.json", timeout=to).json()
        self.abis["AddressManager"] = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/ABIs/AddressManager.sol/AddressManager.json", timeout=to).json()

    def instantiateContract(self, arg: str):
        
        contract = self.w3.eth.contract(self.contracts[arg], abi=self.abis[arg]["abi"])
        return contract
    
    def readStake(self):
        
        sm = self.instantiateContract("StakingManager")
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        if(stakeAmount > Web3.toWei(25, 'ether')):
            return True
        else:
            return False
        
    def StakeManagement(self, transactManager):
        
        contract = self.instantiateContract("EXDT")
        sm = self.instantiateContract("StakingManager")
        
        stakeAmount = sm.functions.AvailableStakedAmountOf(self._AccountAddress).call()
        stakeAllocated = sm.functions.AllocatedStakedAmountOf(self._AccountAddress).call()
        
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
            return True


    
class TransactionManager():    
    def __init__(self, cm):        
        self.netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
        self.w3 = Web3(Web3.HTTPProvider(self.netConfig["_urlSkale"]))
        self.w3Tx = Web3(Web3.HTTPProvider(self.netConfig["_urlTxSkale"]))
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
            if(self.waitingRoom_VIP.qsize() == 0 and self.waitingRoom.qsize() == 0):
                time.sleep(5)
                pass

            else:
                
                try:
                    if(self.waitingRoom_VIP.qsize() != 0):
                        for k_sending_trials in range(3):
                            try:
                                time.sleep(1+k_sending_trials*3.5)
                                increment_tx = self.waitingRoom_VIP.get()                                 
                                previous_nounce = self.w3.eth.get_transaction_count(increment_tx[1])

                                increment_tx[0]["nonce"] = previous_nounce

                                gas = default_gas_amount
                                try:
                                    gasEstimate = self.w3.eth.estimate_gas(increment_tx[0])*1.5
                                    if gasEstimate < 30_000:
                                        gas = gasEstimate + 300_000
                                    elif gasEstimate < 1_000_000:
                                        gas = gasEstimate + 500_000
                                except  Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Gas estimation failed: ",e)

                                increment_tx[0]["gas"] = int(round(int(gas),0))

                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)

                                # SIGN TRANSACTION
                                tx_create = self.w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])

                                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                                tx_hash = self.w3Tx.eth.send_raw_transaction(tx_create.rawTransaction)
                                
                                time.sleep(2)
                                for i in range (10):
                                    time.sleep(i*1.5+1)
                                    # WAIT FOR NEW NOUNCE BY READING PROXY
                                    current_nounce = self.w3.eth.get_transaction_count(increment_tx[1])
                                    if(current_nounce > previous_nounce):
                                        # found a new transaction because account nounce has increased
                                        break

                                # WAIT FOR TX RECEIPT
                                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                                try:       
                                    tx_gasUsed = tx_receipt['gasUsed']
                                    tx_status = int(tx_receipt['status'])
                                    print("\nTriggerValidation ",n_iter," gas limit = ",gas)
                                    tx_status_str = "Failure"
                                    if tx_status == 1 :
                                        tx_status_str = "Success"
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Transaction Status = ", tx_status_str, " , Gas used = ",tx_gasUsed)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Tx Receipt failed : ",e)

            
                                self.last_block = self.w3.eth.get_block('latest')["number"]
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
                                    
                                previous_nounce = self.w3.eth.get_transaction_count(increment_tx[1])

                                increment_tx[0]["nonce"] = previous_nounce
                                gas = default_gas_amount
                                try:
                                    gasEstimate = self.w3.eth.estimate_gas(increment_tx[0])*1.5
                                    if gasEstimate < 30_000:
                                        gas = gasEstimate + 300_000
                                    elif gasEstimate < 1_000_000:
                                        gas = gasEstimate + 500_000
                                except  Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Gas estimation failed: ",e)

                                increment_tx[0]["gas"] = int(round(int(gas),0))
                                                
                                if detailed_validation_printing_enabled:
                                    print("[TRANSACTION MANAGER] Gas = ",increment_tx[0]["gas"])
                                    print("[TRANSACTION MANAGER] tx =>",increment_tx)

                                # SIGN TRANSACTION
                                tx_create = self.w3.eth.account.sign_transaction(increment_tx[0], increment_tx[2])

                                # SEND RAW TRANSACTION VIA THE TX ENDPOINT
                                tx_hash = self.w3Tx.eth.send_raw_transaction(tx_create.rawTransaction)
                                
                                time.sleep(2)
                                for i in range (10):
                                    time.sleep(i*1.5+1)
                                    # WAIT FOR NEW NOUNCE BY READING PROXY
                                    current_nounce = self.w3.eth.get_transaction_count(increment_tx[1])
                                    if(current_nounce > previous_nounce):
                                        # found a new transaction because account nounce has increased
                                        break

                                # WAIT FOR TX RECEIPT
                                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10, poll_latency = 3)
                                try:       
                                    tx_gasUsed = tx_receipt['gasUsed']
                                    tx_status = int(tx_receipt['status'])
                                    print("\nTriggerValidation ",n_iter," gas limit = ",gas)
                                    tx_status_str = "Failure"
                                    if tx_status == 1 :
                                        tx_status_str = "Success"
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Transaction Status = ", tx_status_str, " , Gas used = ",tx_gasUsed)
                                except Exception as e:
                                    if detailed_validation_printing_enabled:
                                        print("[TRANSACTION MANAGER] Tx Receipt failed : ",e)

                                self.last_block = self.w3.eth.get_block('latest')["number"]
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