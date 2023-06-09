import logging
from item import get_item
from models import Processed, LiveConfiguration
from process import process


async def prepare_batch(
    static_configuration, live_configuration: LiveConfiguration
) -> list[Processed]:
    batch_size: int = live_configuration["batch_size"]
    batch: list[Processed] = []
    generator = get_item()
    lab_configuration = static_configuration["lab_configuration"]
    async for item in generator:
        try:
            processed_item: Processed = await process(item, lab_configuration)
            batch.append(processed_item)
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']}"
            )
            if len(batch) == batch_size:
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
