import asyncio, logging
from typing import Callable

from aiosow.perpetuate import on
from aiosow.bindings import wrap, setup
from aiosow.routines import routine
from aiosow.autofill import autofill

from exorde.ipfs import download_ipfs_file, upload_to_ipfs
from exorde.protocol import (
    estimate_gas,
    get_ipfs_hashes_for_batch,
    get_current_work as get_current_work_implementation,
    commit_spot_check,
    is_commit_period_active,
    is_commit_period_over,
    is_reveal_period_active,
    is_reveal_period_over,
)

get_current_work = wrap(lambda batch_id: {"batch_id": batch_id})(
    get_current_work_implementation
)


@setup
def reset_batch_id():
    return {"batch_id": 0}


routine(2, condition=lambda batch_id: not batch_id)(get_current_work)
on("batch_id", condition=lambda batch_id: int(batch_id))(
    wrap(lambda hashes: {"validation_hashes": hashes})(get_ipfs_hashes_for_batch)
)


async def download_files(hashes, memory):
    tasks = [
        autofill(download_ipfs_file, args=[hash], memory=memory) for hash in hashes
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


def validator(function: Callable):
    VALIDATORS.append(function)
    return function


def validator_vote(function: Callable):
    VALIDATORS_VOTES.append(function)
    return function


async def run_validation(items, memory):
    """Runs validators_vote AFTER validators."""
    result = items
    for validator in VALIDATORS:
        result = await autofill(validator, args=[result], memory=memory)
    vote = 1  # by default without validtor in place, the vote is 1
    for validator_vote in VALIDATORS_VOTES:
        vote = validator_vote(items)
        if vote == 0:
            break
    return {"validated": result, "vote": vote, "length": len(result)}


on("validation_hashes")(wrap(lambda files: {"validation_files": files})(download_files))
on("validation_files")(merge_validation_files)
on("merged_validation_file")(run_validation)
on("validated")(
    wrap(lambda cid: {"validation_cid": cid, "commited": False, "batch_id": 0})(
        upload_to_ipfs
    )
)


@setup
def reset_seed():
    return {"seed": None}


@routine(
    5, condition=lambda validation_cid, commited: commited == False and validation_cid
)
async def commit_validation(
    batch_id, validation_cid, vote, length, DataSpotting, memory, worker_key, read_web3
):
    if is_commit_period_active(batch_id, DataSpotting):
        transaction, seed = await commit_spot_check(
            batch_id, validation_cid, vote, length, DataSpotting, memory
        )
        signed_transaction = read_web3.eth.account.sign_transaction(
            transaction, worker_key
        )
        estimated_transaction = await autofill(
            estimate_gas, args=[signed_transaction], memory=memory
        )
        while memory["commit"] != None:
            await asyncio.sleep(1)
        return {"seed": seed, "commited": True, "transaction": estimated_transaction}
    elif is_commit_period_over(batch_id, DataSpotting):
        return {"validation_cid": None, "commited": False}


@routine(5, condition=lambda seed: seed != None)
async def reveal_spot_check(batch_id, validation_cid, vote, seed, DataSpotting):
    if is_reveal_period_active(batch_id, DataSpotting):
        await reveal_spot_check(batch_id, validation_cid, vote, seed, DataSpotting)
        return {"seed": None, "validation_cid": None, "commited": False}
    elif is_reveal_period_over(batch_id, DataSpotting):
        return {"seed": None}
