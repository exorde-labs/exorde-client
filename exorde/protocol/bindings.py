from aiosow.routines import routine, spawn_consumer
from aiosow.bindings import setup, wrap, on, option, expect

from exorde.protocol import (
    reset_signed_transaction,
    worker_address,
    configuration,
    contracts_and_abi_cnf,
    write_web3,
    read_web3,
    contracts,
    select_transaction_to_send,
    send_raw_transaction as send_raw_transaction_implementation,
    nounce,
    reset_transactions,
)

option("ethereum_address", help="Ethereum wallet address", default=None)
# setup the routine consumer
setup(spawn_consumer)

get_nounce = expect(read_web3, retries=2)(wrap(lambda val: {"nounce": val})(nounce))
# nounce is not retrieved in a routine but before new transaction
routine(1, life=5)(get_nounce)

setup(reset_transactions)
# set signed_transaction to None on nounce change
on("nounce")(reset_signed_transaction)

# instanciate workers
setup(
    wrap(lambda acct: {"worker_address": acct.address, "worker_key": acct.key})(
        worker_address
    )
)

# retrieve configuration
setup(configuration)

# retrieve contracts and abi
on("configuration")(contracts_and_abi_cnf)

# choose a url_Skale and instanciate web3
on("configuration")(write_web3)
on("configuration")(read_web3)

# instanciate contracts
on("read_web3")(contracts)

# on transactions or nounce change try to set a new current signed_transaction
no_signed_transaction = lambda signed_transaction: not signed_transaction
on("transactions", condition=no_signed_transaction)(select_transaction_to_send)
on("nounce", condition=no_signed_transaction)(select_transaction_to_send)

send_raw_transaction = send_raw_transaction_implementation
# send_raw_transaction (may have to be a routine)
on("signed_transaction", condition=lambda signed_transaction: signed_transaction)(
    send_raw_transaction
)
