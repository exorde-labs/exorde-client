import logging
import time
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration
from exorde.process import process, TooBigError
from exorde_data import Item
from typing import Union, AsyncGenerator


def evaluate_token_count(__item__: Processed) -> int:
    return 1


def split_item(item: Item) -> list[tuple[int, Item]]:
    return [(1, item)]


async def prepare_batch(
    static_configuration, live_configuration: LiveConfiguration
) -> list[tuple[int, Processed]]:
    max_depth_classification: int = live_configuration["max_depth"]
    batch: list[tuple[int, Processed]] = []  # id, item
    generator: AsyncGenerator[Item, None] = get_item()
    lab_configuration: dict = static_configuration["lab_configuration"]
    i = -1  # every item in the batch is ientified using an ID
    async for item in generator:
        i = i + 1
        try:
            start_time: float = time.perf_counter()
            try:
                processed_item: Processed = await process(
                    item, lab_configuration, max_depth_classification
                )
                batch.append((i, processed_item))
            except TooBigError:
                splitted: list[tuple[int, Item]] = split_item(item)
                for chunk in splitted:
                    processed_chunk: Processed = await process(
                        chunk[1], lab_configuration, max_depth_classification
                    )
                    batch.append((i, processed_chunk))
            end_time: float = time.perf_counter()
            exec_time_s: float = end_time - start_time
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])}"
            )
            if (
                sum(
                    [evaluate_token_count(item) for (__id__, item) in batch]
                )  # this is confused and requires oversight
                >= live_configuration["batch_size"]
            ):
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
