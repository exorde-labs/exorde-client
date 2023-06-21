import logging
import time
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration
from exorde.process import process

async def prepare_batch(
    static_configuration, live_configuration: LiveConfiguration
) -> list[Processed]:
    batch_size: int = live_configuration["batch_size"]
    max_depth_classification: int = live_configuration["max_depth"]
    batch: list[Processed] = []
    generator = get_item()
    lab_configuration = static_configuration["lab_configuration"]
    async for item in generator:
        try:
            
            start_time = time.perf_counter()
            processed_item: Processed = await process(item, lab_configuration, max_depth_classification)
            end_time = time.perf_counter()
            exec_time_s = end_time - start_time
            batch.append(processed_item)
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])}"
            )
            if len(batch) == batch_size:
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
