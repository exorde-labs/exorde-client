
# notes
- si on paye + en gas la requete est priorise
- increment_tx[0] = transaction 
               1  = public_key
               2  = private_key

- utiliser une chaine pour la lecture
           une autre chaine pour l'ecriture

# parametres


# - toutes les 10 minutes 
# https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/transaction_params.json
``` parametrique static defini par exorde
default_gas_amount = 1_200_000 | int
gas_cap_min = 1_200_000 | int
default_gas_price = 100_000 | int

# wait for transaction_receipt
timeout = pendant combien de temps il va le faire
poll_latency ( wait_for_receipt is a while loop that reads)
```

# PREP de la requete 

fait a travers l'api
transaction = contract.function(..., ...)

transactions = [transaction, ...]


# estimate gas
```
gas = estimate_gas = call_reseau ( a eviter ) -> cacher
gas = min_gas if gas < min_gas else gas 
```
chaque fois qu'on transact sur la chaine

```

transaction[0]["gas"] = int(round(int(gas),0))
transaction[0]["gasPrice"] = int(default_gas_price+3) # priority

```

### identifie si une requete a deja ete faite 
```
gas_key_ = (function_bytecode, data_length)

# get the first 4 bytes of the function being called, in the data
function_bytecode = str(transaction[0]["data"])[2:10]
data_length = len(str(transaction[0]["data"]))
```

0. nounce = get_current_nounce(), t = time(), n = 10
1. send(transaction)
2. read current_nounce()
    | > nounce => transaction_ok
    | == nounce && (time() > (t)) + n => transaction_fail

# SIGN TRANSACTION
```
signed_transaction = w3.eth.account.sign_transaction(transaction, private_key_worker)
```


# send_traction
```
    try:
        transaction_hash = w3Tx.eth.send_raw_transaction(signed_transaction.rawTransaction)
    except Exception as e:
        if detailed_validation_printing_enabled:
            print("[TRANSACTION RAW SEND ERROR]: ",e)
            break
```

# wait 

`time.sleep(wait_time)`


# Verification si la transaction est passe
```
# WAIT FOR NEW NOUNCE BY READING PROXY
current_nounce = w3.eth.get_transaction_count(worker_addr)
if(current_nounce > previous_nounce):
    # found a new transaction because account nounce has increased
    break
```

{
    "transaction_to_send" = nounce
    current_nounce = get_current_nounce()
    current_nounce > transaction_to_send:
        transaction_to_send = None
}

overight(transaction_to_send == None)(send_next_transaction)


send_next_transaction = transaction.pop()
