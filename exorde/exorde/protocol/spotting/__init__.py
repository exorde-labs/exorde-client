#! python3.10

from typing import Callable
import logging
from collections import deque
from madframe.autofill import autofill
from importlib import metadata
from datetime import datetime

SIZE = 3


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
from exorde_lab.keywords.models import Keywords
from exorde_lab.translation import translate
from exorde_lab.translation.models import Translation
from exorde_lab.classification import zero_shot
from exorde_lab.classification.models import Classification
from exorde_lab.analysis.models import Analysis
from exorde_lab.analysis import tag
from madframe.bindings import make_async

from madtypes import MadType


class Processed(dict, metaclass=MadType):
    translation: Translation
    top_keywords: Keywords
    classification: Classification
    item: Item


async def pull_to_process(stack, processed, installed_languages, memory):
    try:
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
            logging.error("An error occured classifying an item")
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
        logging.info(f"+ new processed item \t {len(processed)} / 3")
        # technicaly the stack is already updated here
        # we return to trigger the ONS events
        return {"processed": processed, "processing": False, "stack": stack}
    except:
        return {"processing": False, "stack": stack}


from exorde.protocol.models import (
    ProtocolItem,
    ProtocolAnalysis,
    ProcessedItem,
    Batch,
    BatchKindEnum,
)

from exorde.protocol.models import (
    CollectionClientVersion,
    CollectedAt,
    CollectionModule,
)

from enum import Enum


# Custom JSON encoder class
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name  # Serialize Enum value as its name
        return super().default(obj)


async def consume_processed(processed, memory):
    batch: list[Processed] = [processed.pop(0) for _ in range(SIZE)]
    analysis_results: list[Analysis] = await autofill(
        tag,
        args=[[processed.translation.translation for processed in batch]],
        memory=memory,
    )
    complete_processes: list[ProcessedItem] = []
    for processed, analysis in zip(batch, analysis_results):
        prot_item = ProtocolItem(
            created_at=processed.item.created_at,
            domain=processed.item.domain,
            url=processed.item.url,
            language=processed.translation.language,
        )

        if processed.item.title:
            prot_item.title = processed.item.title
        if processed.item.summary:
            prot_item.summary = processed.item.summary
        if processed.item.picture:
            prot_item.picture = processed.item.picture
        if processed.item.author:
            prot_item.author = processed.item.author
        if processed.item.external_id:
            prot_item.external_id = processed.item.external_id
        if processed.item.external_parent_id:
            prot_item.external_parent_id = processed.item.external_parent_id
        completed = ProcessedItem(
            item=prot_item,
            analysis=ProtocolAnalysis(
                classification=processed.classification,
                top_keywords=processed.top_keywords,
                language_score=analysis.language_score,
                gender=analysis.gender,
                sentiment=analysis.sentiment,
                embedding=analysis.embedding,
                source_type=analysis.source_type,
                text_type=analysis.text_type,
                emotion=analysis.emotion,
                irony=analysis.irony,
                age=analysis.age,
            ),
            collection_client_version=CollectionClientVersion(
                f"exorde:v.{metadata.version('exorde_data')}"
            ),
            collection_module=CollectionModule("unknown"),
            collected_at=CollectedAt(datetime.now().isoformat() + "Z"),
        )
        complete_processes.append(completed)
    result_batch: Batch = Batch(
        items=complete_processes, kind=BatchKindEnum.SPOTTING
    )
    print()
    print()
    print()
    print(json.dumps(result_batch, indent=4, cls=EnumEncoder))
    print()
    print()
    print()

    return {"batch_to_consume": result_batch, "processed": processed}


def reset_cids():
    return {"cids": [], "current_cid_commit": None}


def push_new_cid(value, cids):
    return {"cids": cids + [value["cid"]]}


def choose_cid_to_commit(cids):
    return {"current_cid_commit": cids[0], "cids": cids[1:]}
