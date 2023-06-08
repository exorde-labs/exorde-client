from exorde_data import query
from functools import wraps
import logging

from typing import Callable

from madframe.bindings import alias, wire, autofill
from madframe.routines import routine
from exorde.scraping import generate_url

broadcast_formated_when, on_formated_data_do = wire(perpetual=True)


def infinite_generator(condition: Callable):
    def _generator_consumer(function: Callable):
        """Re-autofill a generator function at end of it's loop"""

        iterated = None

        @wraps(function)
        async def __generator_consumer(*args, **kwargs):
            nonlocal iterated
            while await autofill(condition, args=args, **kwargs):
                if not iterated:
                    iterated = await autofill(function, args=args, **kwargs)
                try:
                    return await iterated.__anext__()
                except StopAsyncIteration as error:
                    logging.exception(error)
                    iterated = await autofill(function, args=args, **kwargs)
                    return await iterated.__anext__()

        return __generator_consumer

    return _generator_consumer


alias("url")(generate_url)
scrap = infinite_generator(lambda: True)(query)
routine(0.2, perpetuate=False, condition=lambda processing: not processing)(
    broadcast_formated_when(scrap)
)


__all__ = ["broadcast_formated_when", "on_formated_data_do"]
