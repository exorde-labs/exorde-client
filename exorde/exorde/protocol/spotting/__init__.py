#! python3.10

from typing import Callable
import logging
from collections import deque
from madframe.autofill import autofill

SIZE = 25


def init_stack():
    return {"stack": deque(maxlen=SIZE), "processed": [], "processing": False}


FILTERS = []


def filter(function: Callable):
    FILTERS.append(function)
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
from exorde_data.models import Item
from exorde_lab.preprocess import preprocess
from exorde_lab.keywords import populate_keywords
from exorde_lab.keywords.models import TopKeywords
from exorde_lab.translation import translate
from exorde_lab.translation.models import Translation
from exorde_lab.classification import zero_shot
from exorde_lab.classification.models import Classification

from madframe.bindings import make_async

from madtypes import MadType


class Processed(dict, metaclass=MadType):
    translation: Translation
    top_keywords: TopKeywords
    classification: Classification
    item: Item


async def pull_to_process(stack, processed, installed_languages, memory):
    item: Item = stack.pop()
    memory["processing"] = True
    memory["stack"] = stack
    try:
        item = preprocess(item, False)
    except Exception as err:
        logging.error("An error occured pre-processing an item")
        logging.error(err)
        logging.error(json.dumps(item, indent=4))
        raise err

    try:
        translation: Translation = translate(item, installed_languages)
    except Exception as err:
        logging.error("An error occured translating an item")
        logging.error(err)
        logging.error(json.dumps(item, indent=4))
        raise err

    try:
        top_keywords: TopKeywords = populate_keywords(translation)
    except Exception as err:
        logging.error("An error occured populating keywords for an item")
        logging.error(err)
        logging.error(json.dumps(item, indent=4))
        raise err

    try:
        classification: Classification = await autofill(
            make_async(zero_shot), args=[translation], memory=memory
        )
    except Exception as err:
        logging.error("An error occured translating an item")
        logging.error(err)
        logging.error(json.dumps(item, indent=4))
        raise err

    processing_batch: Processed = Processed(
        item=item,
        translation=translation,
        top_keywords=top_keywords,
        classification=classification,
    )

    processed.append(processing_batch)
    logging.info(f"+ new processed item \t {len(processed)} / 25")
    # technicaly the stack is already updated here
    # we return to trigger the ONS events
    return {"processed": processed, "processing": False, "stack": stack}


async def consume_processed(processed, memory):
    batch: list[Processed] = [processed.pop(0) for _ in range(SIZE)]
    print("HEEERE")
    return {"batch_to_consume": formated_batch, "processed": processed}


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}
