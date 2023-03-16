'''
Composition for EXD Mining.

IDEAS:
    - await lock(variable_name) <- will lock a function execution until
      variable_name changes in the same spirit of on
TODOS:
    - multiple workers
    ---
    - check for main eth address
    - cache
    - smoother request frequency
'''
from aiosow.bindings import on, wrap, wire
from aiosow.routines import routine

from aiosow_twitter.bindings import tweets

from exorde import *

# instanciate workers
routine(0, life=-1)(wrap(lambda addr, key: {
    'worker_address': addr, 'worker_key': key
})(worker_address))

# retrieve configuration
routine(60 * 5, life=0)(configuration)

# retrieve contracts and abi
on('configuration')(contracts_and_abi_cnf)

# choose a url_Skale and instanciate web3
on('configuration')(write_web3)
on('configuration')(read_web3)

# instanciate contracts
on('read_web3')(contracts)

# on transactions or nounce change try to set a new current signed_transaction
no_signed_transaction = lambda signed_transaction: not signed_transaction
on('transactions', condition=no_signed_transaction)(select_transaction_to_send)
on('nounce', condition=no_signed_transaction)(select_transaction_to_send)

# send_raw_transaction (may have to be a routine)
on('signed_transaction', condition=lambda signed_transaction: signed_transaction)(
    send_raw_transaction
)

# nounce is retrieved every secondition
routine(100, life=5)(wrap(lambda val: {'nounce': val})(nounce))

# set signed_transaction to None on nounce change
on('nounce')(lambda: { 'signed_transaction': None })

broadcast_formated, formated = wire()
# tweet retrieval
tweets(broadcast_formated(twitter_to_exorde_format))

