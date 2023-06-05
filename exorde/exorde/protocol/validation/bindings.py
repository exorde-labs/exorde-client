import asyncio, logging
from typing import Callable

from madframe.perpetuate import on
from madframe.bindings import wrap, setup
from madframe.routines import routine
from madframe.autofill import autofill

from exorde.protocol.ipfs import download_ipfs_file, upload_to_ipfs
from exorde.protocol.base import (
    estimate_gas,
    get_ipfs_hashes_for_batch,
    get_current_work as get_current_work_implementation,
    commit_spot_check,
    is_commit_period_active,
    is_commit_period_over,
    is_reveal_period_active,
    is_reveal_period_over,
    reveal_spot_check as do_reveal_spot_check,
)


get_current_work = wrap(
    lambda result: {
        "batch_id": result[0],
        "previous_batch_id": result[0] if result[0] != 0 else result[1],
    }
)(get_current_work_implementation)


@setup
def reset_batch_id():
    return {"batch_id": 0, "previous_batch_id": 0}


routine(2, condition=lambda batch_id: not batch_id)(get_current_work)
on("batch_id", condition=lambda batch_id: int(batch_id))(
    wrap(lambda hashes: {"validation_hashes": hashes})(
        get_ipfs_hashes_for_batch
    )
)


async def download_files(hashes, memory):
    tasks = [
        autofill(download_ipfs_file, args=[hash], memory=memory)
        for hash in hashes
    ]
    files = await asyncio.gather(*tasks)
    return [file for file in files if file]


@wrap(lambda result: {"merged_validation_file": result})
async def merge_validation_files(validation_files):
    logging.debug(validation_files)
    return {
        "ValidationContent": [
            entity for file in validation_files for entity in file["Content"]
        ]
    }


VALIDATORS = []
VALIDATORS_VOTES = []
BATCH_APPLICATORS = []


def validator(function: Callable):
    VALIDATORS.append(function)
    return function


def validator_vote(function: Callable):
    VALIDATORS_VOTES.append(function)
    return function


def batch_applicator(function: Callable):
    BATCH_APPLICATORS.append(function)


async def run_validation(batch, memory):
    """Runs validators_vote AFTER validators."""
    items = batch["ValidationContent"]
    for validator in VALIDATORS:
        items = await autofill(validator, args=[items], memory=memory)
    vote = 1  # by default without validtor in place, the vote is 1
    for validator_vote in VALIDATORS_VOTES:
        vote = validator_vote(items)
        if vote == 0:
            break

    batch["ValidationContent"] = items
    return {"validated": batch, "vote": vote, "length": len(items)}


on("validation_hashes")(
    wrap(lambda files: {"validation_files": files})(download_files)
)
on("validation_files")(merge_validation_files)
on("merged_validation_file")(run_validation)
on("validated")(
    wrap(lambda cid: {"validation_cid": cid["cid"], "commited": False})(
        upload_to_ipfs
    )
)


@setup
def reset_seed():
    return {"seed": None}


@routine(
    5,
    condition=lambda validation_cid, commited: commited == False
    and validation_cid,
)
async def commit_validation(
    batch_id,
    validation_cid,
    vote,
    length,
    DataSpotting,
    memory,
    worker_key,
    read_web3,
    nonce,
    worker_address,
):
    if await is_commit_period_active(batch_id, DataSpotting):
        transaction, seed = await commit_spot_check(
            batch_id, validation_cid, vote, length, DataSpotting, memory
        )
        transaction = await transaction.build_transaction(
            {"from": worker_address, "gasPrice": 100_000, "nonce": nonce}
        )
        estimated_transaction = await autofill(
            estimate_gas, args=[transaction], memory=memory
        )
        signed_transaction = read_web3.eth.account.sign_transaction(
            estimated_transaction, worker_key
        )

        return {
            "seed": seed,
            "commited": True,
            "transaction": signed_transaction,
        }
    elif await is_commit_period_over(batch_id, DataSpotting):
        return {"validation_cid": None, "commited": False, "batch_id": 0}


@routine(5, condition=lambda seed: seed != None)
async def reveal_spot_check(
    batch_id,
    validation_cid,
    vote,
    seed,
    DataSpotting,
    worker_address,
    nonce,
    memory,
    read_web3,
    worker_key,
):
    if await is_reveal_period_active(batch_id, DataSpotting):
        transaction = await do_reveal_spot_check(
            batch_id, validation_cid, vote, seed, DataSpotting
        )

        transaction = await transaction.build_transaction(
            {"from": worker_address, "gasPrice": 100_000, "nonce": nonce}
        )
        estimated_transaction = await autofill(
            estimate_gas, args=[transaction], memory=memory
        )
        signed_transaction = read_web3.eth.account.sign_transaction(
            estimated_transaction, worker_key
        )
        return {
            "seed": None,
            "validation_cid": None,
            "commited": False,
            "batch_id": 0,
            "transaction": signed_transaction,
        }
    elif await is_reveal_period_over(batch_id, DataSpotting):
        return {"seed": None}
