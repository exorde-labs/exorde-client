"""
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S
  
  Supported composition for EXD mining.
"""

import logging
from aiosow.bindings import setup, call_limit, wire
from aiosow.perpetuate import on
from aiosow.autofill import autofill

from exorde.twitter.bindings import on_formated_tweet_do

from typing import Callable
from exorde.ipfs.bindings import push_to_ipfs, on_new_cid_do
from exorde.protocol.bindings import commit_current_cid
from exorde.spot import (
    push_to_stack,
    log_stack_len,
    consume_stack,
    reset_cids,
    push_new_cid,
    choose_cid_to_commit,
)


SPOTTING_PROCCESES: list[Callable] = []


def spotting(function: Callable):
    SPOTTING_PROCCESES.append(function)
    return function


setup(reset_cids)


spotting_ran_when, on_spotting_done_do = wire(perpetual=True)


@on_formated_tweet_do
@spotting_ran_when
async def run_spotting(item: dict, memory):
    for process in SPOTTING_PROCCESES:
        item = await autofill(
            process,
            args=[
                item,
            ],
            memory=memory,
        )
    return item


on_spotting_done_do(push_to_stack)


on("stack")(call_limit(1)(log_stack_len))
on("stack")(consume_stack)
on("batch_to_consume", condition=lambda value, transaction: value and not transaction)(
    push_to_ipfs
)
on_new_cid_do(push_new_cid)
on("cids", condition=lambda cids: len(cids))(
    lambda __cids__: logging.info(f"A batch has been uploaded to IPFS")
)
on(
    "cids",
    condition=lambda cids, current_cid_commit: len(cids) and not current_cid_commit,
)(choose_cid_to_commit)
on_new_cid_to_commit = on("current_cid_commit", condition=lambda value: value)
on_new_cid_to_commit(
    lambda value: logging.info(
        f"New CID has been choosen for ritual transaction ({value})"
    )
)
on_new_cid_to_commit(commit_current_cid)
