import logging
import time
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration
from exorde.process import process, TooBigError
from exorde_data import Item, Content
from typing import AsyncGenerator


def evaluate_token_count(__item__: Processed) -> int:
    return 1


def split_string_into_chunks(string, chunk_size):
    return [
        string[i : i + chunk_size] for i in range(0, len(string), chunk_size)
    ]


def split_item(item: Item, max_token_count: int) -> list[Item]:
    if not item.content or len(item.content) <= max_token_count:
        return [item]
    else:
        return [
            Item(
                content=Content(chunk),
                author=item.author,
                created_at=item.created_at,
                domain=item.domain,
                url=item.url,
            )
            for chunk in split_string_into_chunks(
                item.content, max_token_count
            )
        ]


async def prepare_batch(
    static_configuration, live_configuration: LiveConfiguration
) -> list[tuple[int, Processed]]:
    max_depth_classification: int = live_configuration["max_depth"]
    batch: list[tuple[int, Processed]] = []  # id, item
    generator: AsyncGenerator[Item, None] = get_item()
    lab_configuration: dict = static_configuration["lab_configuration"]
    item_id = -1
    async for item in generator:
        item_id = item_id + 1
        try:
            start_time: float = time.perf_counter()
            try:
                processed_item: Processed = await process(
                    item, lab_configuration, max_depth_classification
                )
                batch.append((item_id, processed_item))
            except TooBigError:
                splitted: list[Item] = split_item(
                    item,
                    static_configuration["lab_configuration"][
                        "max_token_count"
                    ],
                )
                for chunk in splitted:
                    processed_chunk: Processed = await process(
                        chunk, lab_configuration, max_depth_classification
                    )
                    batch.append((item_id, processed_chunk))
            end_time: float = time.perf_counter()
            exec_time_s: float = end_time - start_time
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])}"
            )
            if (
                sum([evaluate_token_count(item) for (__id__, item) in batch])
                >= live_configuration["batch_size"]
            ):
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
