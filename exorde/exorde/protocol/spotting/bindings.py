import logging
from madframe.bindings import setup, wire
from madframe.perpetuate import on

from exorde.scraping.bindings import on_formated_data_do

from exorde.protocol.ipfs.bindings import push_to_ipfs, on_new_cid_do
from exorde.protocol.base.bindings import commit_current_cid
from exorde.protocol.spotting import (
    push_to_stack,
    consume_processed,
    pull_to_process,
)


# event(success, failure)


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}


def init_stack():
    return {"stack": [], "processed": [], "processing": False}


setup(init_stack)
setup(reset_cids)


spotting_ran_when, on_spotting_done_do = wire(perpetual=True)


on_formated_data_do(push_to_stack)

from madframe.routines import routine

routine(60)(init_stack)

on(
    "stack",
    condition=lambda stack, processing, running: len(stack) >= 1
    and not processing
    and running,
)(pull_to_process)
on("processed")(lambda processed: f"{len(processed)} processed items")
# idk why this line does not trigger
on("processed", condition=lambda processed: len(processed) == 50)(
    consume_processed
)
on(
    "processed",
    lambda processed: logging.info("processed: %d", len(processed)),
)
on(
    "batch_to_consume",
    condition=lambda value, transaction, batch_id: value
    and not transaction
    and not batch_id,
)(push_to_ipfs)
on_new_cid_do(push_new_cid)
on("cids", condition=lambda cids: len(cids))(
    lambda __cids__: logging.info(f"A batch has been uploaded to IPFS")
)
on(
    "cids",
    condition=lambda cids, current_cid_commit: len(cids)
    and not current_cid_commit,
)(choose_cid_to_commit)
on_new_cid_to_commit = on("current_cid_commit", condition=lambda value: value)
on_new_cid_to_commit(
    lambda value: logging.info(
        f"New CID has been choosen for ritual transaction ({value})"
    )
)
on_new_cid_to_commit(commit_current_cid)
