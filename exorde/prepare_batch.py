import logging
import time
import argparse
from typing import AsyncGenerator
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration, StaticConfiguration
from exorde.process import process
from exorde_data import Item


def evaluate_token_count(content: str):
    return 1


async def prepare_batch(
    static_configuration: StaticConfiguration,
    live_configuration: LiveConfiguration,
    command_line_arguments: argparse.Namespace,
) -> list[Processed]:
    max_depth_classification: int = live_configuration["max_depth"]
    batch: list[Processed] = []
    generator: AsyncGenerator[Item, None] = get_item(command_line_arguments)
    lab_configuration = static_configuration["lab_configuration"]
    async for item in generator:
        try:
            start_time = time.perf_counter()
            processed_item: Processed = await process(
                item, lab_configuration, max_depth_classification
            )
            end_time = time.perf_counter()
            exec_time_s = end_time - start_time
            batch.append(processed_item)
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])}"
            )
            if (
                sum(
                    [evaluate_token_count(item.item.content) for item in batch]
                )
                >= live_configuration["batch_size"]
            ):
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
