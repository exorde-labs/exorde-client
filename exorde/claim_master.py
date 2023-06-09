async def claim_master(
    main_address_to_claim, worker_account, contracts, write_web3, read_web3
):
    nonce = await read_web3.eth.get_transaction_count(worker_account.address)

    transaction = (
        contracts["AddressManager"]
        .functions.ClaimMaster(main_address_to_claim)
        .build_transaction(
            {
                "nonce": nonce,
                "from": worker_account.address,
            }
        )
    )
    signed_transaction = read_web3.eth.account.sign_transaction(
        transaction, worker_account.key.hex()
    )
    transaction_hash = await write_web3.eth.send_raw_transaction(
        signed_transaction.rawTransaction
    )
    return transaction_hash, nonce
