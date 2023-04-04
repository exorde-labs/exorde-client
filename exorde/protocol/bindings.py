from aiosow.bindings import setup, wrap, on, option, expect, chain, alias

from exorde.protocol import (
    worker_address,
    configuration,
    contracts_and_abi_cnf,
    write_web3,
    read_web3,
    contracts,
    send_raw_transaction as send_raw_transaction_implementation,
    nonce,
    reset_transaction,
    spot_data,
    build_transaction,
)

option("ethereum_address", help="Ethereum wallet address", default=None)

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

# choose an url_Skale and instanciate web3
on("configuration")(write_web3)
on("configuration")(read_web3)

# instanciate contracts
on("read_web3")(contracts)

get_nonce = expect(read_web3, retries=2)(nonce)
alias("nonce")(get_nonce)
# nonce is not retrieved in a routine but before new transaction
# routine(1, timeout=5)(get_nonce)

setup(reset_transaction)
# set signed_transaction to None on nonce change
# on("nonce")(reset_signed_transaction)

# on transactions or nonce change try to set a new current signed_transaction
# no_signed_transaction = lambda signed_transaction: not signed_transaction
# on("transactions", condition=no_signed_transaction)(select_transaction_to_send)
# on("nonce", condition=no_signed_transaction)(select_transaction_to_send)

send_raw_transaction = send_raw_transaction_implementation
# send_raw_transaction (may have to be a routine)
# on("signed_transaction", condition=lambda signed_transaction: signed_transaction)(
#    send_raw_transaction
# )
push_new_transaction = wrap(lambda transaction: {"transaction": transaction})
commit_current_cid = push_new_transaction(chain(spot_data, build_transaction))
