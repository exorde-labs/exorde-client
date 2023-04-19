import logging
from aiosow.bindings import (
    setup,
    wrap,
    on,
    option,
    expect,
    chain,
    alias,
    until_success,
    delay,
)
from aiosow.routines import routine

from exorde.protocol import (
    check_provided_user_address,
    get_balance,
    select_random_faucet,
    sign_transaction,
    worker_address,
    configuration,
    contracts_and_abi_cnf,
    write_web3,
    read_web3,
    contracts,
    send_raw_transaction,
    nonce,
    spot_data,
    build_transaction,
    init_gas_cache,
    estimate_gas,
    faucet,
    log_current_rep,
    register,
)

option("user_address", help="Ethereum wallet address", default=None)
routine(5 * 60)(log_current_rep)
# instanciate workers
setup(
    wrap(lambda acct: {"worker_address": acct.address, "worker_key": acct.key})(
        worker_address
    )
)
setup(configuration)
setup(init_gas_cache)
setup(check_provided_user_address)
setup(wrap(lambda value: {"balance": value})(get_balance))
alias("selected_faucet")(select_random_faucet)
on("balance", condition=lambda value: value == 0)(until_success(delay(1)(faucet)))
# retrieve contracts and abi
on("configuration")(contracts_and_abi_cnf)

# choose an url_Skale and instanciate web3
on("configuration")(write_web3)
on("configuration")(read_web3)

# instanciate contracts
on("read_web3")(contracts)

get_nonce = expect(read_web3, retries=2)(nonce)
alias("nonce")(get_nonce)

push_new_transaction = wrap(lambda transaction: {"transaction": transaction})
commit_current_cid = push_new_transaction(
    chain(spot_data, build_transaction, estimate_gas, sign_transaction)
)

setup(chain(register, build_transaction))

on("transaction")(
    lambda transaction: logging.debug(f"Current transaction: {transaction}")
)
on(
    "transaction",
    condition=lambda value: value,
)(send_raw_transaction)
