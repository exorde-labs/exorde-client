#! python3.10

import logging
from collections import deque
from aiosow.command import run
from datetime import datetime, timedelta, timezone

# 2. on('stack', condition: lambda stack: len(stack) >= 100)
# 3. build transaction & push to transaction manager


def reset_stack():
    return {"stack": deque(maxlen=1000)}


def push_to_stack(value, stack):
    if datetime.fromisoformat(value["item"]["CreationDateTime"]) - datetime.now(
        timezone.utc
    ) > timedelta(seconds=180):
        return {}
    if value not in stack:
        stack.append(value)
        # technicaly the stack is already updated here
        # we return to trigger the ONS events
        return {"stack": stack}
    else:
        # if we had keyword we could weight in the duplicates in keyword choice
        # we could also trigger page roll after a certain amount of duplicates
        # but we should be able to pass on this option to be able to "monitor"
        # specific items
        logging.debug("Duplicate collection")


def log_stack_len(stack):
    logging.debug(f"{len(stack)} items ready to be processed")


SIZE = 100


def consume_stack(stack):
    if len(stack) < SIZE:
        return
    return {"batch_to_consume": [stack.popleft() for _ in range(SIZE)], "stack": stack}


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}


launch = lambda: run("exorde")
