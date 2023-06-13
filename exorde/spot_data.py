from exorde.estimate_gas import estimate_gas


async def spot_data(
    cid,
    worker_account,
    configuration,
    gas_cache,
    contracts,
    read_web3,
    write_web3,
):
    previous_nonce = await read_web3.eth.get_transaction_count(
        worker_account.address
    )
    assert isinstance(cid, str)
    transaction = await (
        contracts["DataSpotting"]
        .functions.SpotData([cid], [""], [configuration["batch_size"]], "")
        .build_transaction(
            {
                "nonce": previous_nonce,
                "from": worker_account.address,
                "gasPrice": configuration["default_gas_price"],
            }
        )
    )

    estimated_transaction = await estimate_gas(
        transaction, read_web3, gas_cache, configuration
    )

    signed_transaction = read_web3.eth.account.sign_transaction(
        estimated_transaction, worker_account.key.hex()
    )
    transaction_hash = await write_web3.eth.send_raw_transaction(
        signed_transaction.rawTransaction
    )

    return transaction_hash, previous_nonce
