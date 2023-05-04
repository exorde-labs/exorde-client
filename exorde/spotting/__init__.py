#! python3.10

from typing import Callable
import logging
from collections import deque
from aiosow.autofill import autofill


def init_stack():
    return {"stack": deque(maxlen=100)}


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
        filter_result = await autofill(filter_function, args=[value], memory=memory)
        if filter_result == False:
            break

    if filter_result:
        for applicator in APPLICATORS:
            value = await autofill(applicator, args=[value], memory=memory)

        stack.append(value)
        # technicaly the stack is already updated here
        # we return to trigger the ONS events
        return {"stack": stack}
    else:
        return {}


def log_stack_len(stack):
    logging.info(f"{len(stack)} items in memory")


SIZE = 100
BATCH_APPLICATORS = []


def batch_applicator(function: Callable) -> Callable:
    BATCH_APPLICATORS.append(function)
    return function


async def consume_stack(stack, memory):
    batch = [stack.popleft() for _ in range(SIZE)]
    for batch_applicator in BATCH_APPLICATORS:
        result = await autofill(batch_applicator, args=[batch], memory=memory)
        batch = zip(batch, result)
    print(batch)
    return {"batch_to_consume": batch, "stack": stack}


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}
