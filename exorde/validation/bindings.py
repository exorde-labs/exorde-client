import asyncio
from typing import Callable

from aiosow.perpetuate import on
from aiosow.bindings import wire, wrap, setup
from aiosow.routines import routine
from aiosow.autofill import autofill

from exorde.ipfs import download_ipfs_file, upload_to_ipfs
from exorde.protocol import (
    get_ipfs_hashes_for_batch,
    is_new_work_available,
    get_current_work,
    commit_spot_check,
    is_commit_period_active,
    is_commit_period_over,
    is_reveal_period_active,
    is_reveal_period_over,
)

broadcast_new_job_available, on_new_job_available_do = wire(perpetual=True)
routine(2)(broadcast_new_job_available(is_new_work_available))
on_new_job_available_do(wrap(lambda batch_id: {"batch_id": batch_id})(get_current_work))

on("batch_id")(
    wrap(lambda hashes: {"validation_hashes": hashes})(get_ipfs_hashes_for_batch)
)


async def download_files(hashes, memory):
    tasks = [
        autofill(download_ipfs_file, args=[hash], memory=memory) for hash in hashes
    ]
    files = await asyncio.gather(*tasks)
    return files


@wrap(lambda result: {"merged_validation_file": result})
async def merge_validation_files(validation_files):
    return [entity for file in validation_files for entity in file["Content"]]


VALIDATORS = []
VALIDATORS_VOTES = []


def validator(function: Callable):
    VALIDATORS.append(function)
    return function


def validator_vote(function: Callable):
    VALIDATORS_VOTES.append(function)
    return function


@wrap(
    lambda validated, vote, length: {
        "validated": validated,
        "vote": vote,
        "length": length,
    }
)
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
    return (result, vote, len(result))


on("validation_hashes")(wrap(lambda files: {"validation_files": files})(download_files))
on("validation_files")(merge_validation_files)
on("merged_validation_file")(run_validation)
on("validated")(
    wrap(lambda cid: {"validation_cid": cid, "commited": False})(upload_to_ipfs)
)


@setup
def reset_seed():
    return {"seed": None}


@routine(
    5, condition=lambda validation_cid, commited: commited == False and validation_cid
)
async def commit_validation(
    batch_id, validation_cid, vote, length, DataSpotting, memory
):
    if is_commit_period_active(batch_id, DataSpotting):
        __transaction__, seed = await commit_spot_check(
            batch_id, validation_cid, vote, length, DataSpotting, memory
        )
        return {"seed": seed, "commited": True}
    elif is_commit_period_over(batch_id, DataSpotting):
        return {"validation_cid": None, "commited": False}


@routine(5, condition=lambda seed: seed != None)
async def reveal_spot_check(batch_id, validation_cid, vote, seed, DataSpotting):
    if is_reveal_period_active(batch_id, DataSpotting):
        await reveal_spot_check(batch_id, validation_cid, vote, seed, DataSpotting)
        return {"seed": None, "validation_cid": None, "commited": False}
    elif is_reveal_period_over(batch_id, DataSpotting):
        return {"seed": None}
