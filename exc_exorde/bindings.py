'''
Composition for EXD Mining.

IDEAS:
    - await lock(variable_name) <- will lock a function execution until
      variable_name changes in the same spirit of oversight
TODOS:
    - multiple workers
    ---
    - check for main eth address
    - cache
    - smoother request frequency
'''
from exorde.bindings import routine, oversight, wrap

from exc_twitter import bindings as __bindings__
from exc_twitter import tweet_wire

from exc_exorde import *

# instanciate workers
routine(0, timeout=-1)(wrap(lambda addr, key: {
    'worker_address': addr, 'worker_key': key
})(worker_address))

# retrieve configuration
routine(60 * 5, timeout=0)(configuration)

# retrieve contracts and abi
oversight('configuration')(contracts_and_abi_cnf)

# choose a url_Skale and instanciate web3
oversight('configuration')(write_web3)
oversight('configuration')(read_web3)

# instanciate contracts
oversight('read_web3')(contracts)

# on transactions or nounce change try to set a new current signed_transaction
no_signed_transaction = lambda signed_transaction: not signed_transaction
oversight('transactions', cond=no_signed_transaction)(select_transaction_to_send)
oversight('nounce', cond=no_signed_transaction)(select_transaction_to_send)

# send_raw_transaction (may have to be a routine)
oversight('signed_transaction', cond=lambda signed_transaction: signed_transaction)(
    send_raw_transaction
)

# nounce is retrieved every second
routine(1, timeout=5)(wrap(lambda val: {'nounce': val})(nounce))

# set signed_transaction to None on nounce change
oversight('nounce')(lambda: { 'signed_transaction': None })

# tweet retrieval
tweet_wire(twitter_to_exorde_format)

formated_tweet_trigger, formated_tweet_wire = wire(batch=100)
