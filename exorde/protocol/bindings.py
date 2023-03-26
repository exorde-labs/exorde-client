from aiosow.routines import routine
from aiosow.bindings import setup, wrap, on, option

from exorde.protocol import (
    worker_address,
    configuration,
    contracts_and_abi_cnf,
    write_web3,
    read_web3,
    contracts,
    select_transaction_to_send,
    send_raw_transaction,
)

option("ethereum_address", help="Ethereum wallet address", default=None)
# nounce is retrieved every second, initial life set to 5 for setup time
# routine(1, life=5)(wrap(lambda val: {'nounce': val})(nounce))

# set signed_transaction to None on nounce change
on("nounce")(lambda: {"signed_transaction": None})


# instanciate workers
setup(
    wrap(lambda acct: {"worker_address": acct.address, "worker_key": acct.key})(
        worker_address
    )
)

# retrieve configuration
routine(60 * 5, life=0)(configuration)

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

# send_raw_transaction (may have to be a routine)
on("signed_transaction", condition=lambda signed_transaction: signed_transaction)(
    send_raw_transaction
)
