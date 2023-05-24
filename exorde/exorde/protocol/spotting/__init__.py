#! python3.10

from typing import Callable
import logging
from collections import deque
from aiosow.autofill import autofill

SIZE = 25


def init_stack():
    return {"stack": deque(maxlen=SIZE), "processed": [], "processing": False}


FILTERS = []
APPLICATORS = []


def filter(function: Callable):
    FILTERS.append(function)
    return function


def applicator(function: Callable):
    APPLICATORS.append(function)
    return function


async def push_to_stack(value, stack, memory):
    filter_result = True
    for filter_function in FILTERS:
        filter_result = await autofill(
            filter_function, args=[value], memory=memory
        )
        if filter_result == False:
            break
    if filter_result:
        stack.append(value)
        return {"stack": stack}


import json


async def pull_to_process(stack, processed, memory):
    value = stack.pop()
    memory["processing"] = True
    memory["stack"] = stack
    try:
        for applicator in APPLICATORS:
            value = await autofill(applicator, args=[value], memory=memory)
        processed.append(value)
        logging.info(f"+ new processed item \t {len(processed)} / 25")
        # technicaly the stack is already updated here
        # we return to trigger the ONS events
        return {"processed": processed, "processing": False}
    except Exception as err:
        logging.error("An error occured processing an item")
        logging.error(err)
        logging.error(json.dumps(value, indent=4))


BATCH_APPLICATORS = []


def batch_applicator(function: Callable) -> Callable:
    BATCH_APPLICATORS.append(function)
    return function


async def consume_processed(processed, memory):
    batch = [processed.pop(0) for _ in range(SIZE)]
    logging.info("applying batch applicators...")
    for batch_applicator in BATCH_APPLICATORS:
        batch = await autofill(batch_applicator, args=[batch], memory=memory)
    logging.info("...batch applicators ok")
    print(batch)
    return {"batch_to_consume": batch, "processed": processed}


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}
