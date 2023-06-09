import logging
from item import get_item
from models import Processed, Configuration
from process import process


async def prepare_batch(
    batch_size: int, lab_configuration, configuration: Configuration
) -> list[Processed]:
    batch: list[Processed] = []
    generator = get_item()
    async for item in generator:
        try:
            processed_item: Processed = await process(item, lab_configuration)
            batch.append(processed_item)
            logging.info(
                f" + A new item has been processed {len(batch)}/{configuration['batch_size']}"
            )
            if len(batch) == batch_size:
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
