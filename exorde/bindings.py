'''
Composition for EXD Mining.

TODOS:
    - check for main eth address
    - cache
    - smoother request frequency
'''

from aiosow.bindings import on, wrap, wire, option, alias, accumulator, setup
from aiosow.routines import routine, spawn_consumer

from aiosow_twitter.bindings import on_tweet_reception_do
from aiosow.http import aiohttp_session

from exorde import *

option('ethereum_address', help='Ethereum wallet address', default=None)

# setup an aiohttp session for ipfs upload
setup(wrap(lambda session: { 'session': session })(aiohttp_session))
setup(wrap(lambda schema: { 'ipfs_schema': schema })(load_json_schema))
alias('ipfs_path')(lambda: 'http://ipfs-api.exorde.network/add')

# instanciate workers
setup(wrap(lambda acct: {
    'worker_address': acct.address, 'worker_key': acct.key
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

# nounce is retrieved every second, initial life set to 5 for setup time
# routine(1, life=5)(wrap(lambda val: {'nounce': val})(nounce))

# set signed_transaction to None on nounce change
on('nounce')(lambda: { 'signed_transaction': None })

# tweet retrieval and format
broadcast_formated, on_formated_tweet_do = wire()
on_tweet_reception_do(broadcast_formated(twitter_to_exorde_format))

# batching
broadcast_batch_ready, on_batch_ready_do = wire()
build_batch = broadcast_batch_ready(accumulator(10)(spot_block))

# when a tweet is formated, push it to batch preparation
on_formated_tweet_do(build_batch)

# when a batch is ready, upload it to ipfs
broadcast_new_valid_batch, on_new_valid_batch_do = wire()
on_batch_ready_do(broadcast_new_valid_batch(validate_batch_schema))

broadcast_new_cid, on_new_cid_do = wire()
on_new_valid_batch_do(broadcast_new_cid(upload_to_ipfs))

on_new_cid_do(lambda value: print(value))

setup(spawn_consumer)
