from . import urls
from madframe.bindings import autofill
import random


async def generate_url(memory):
    generator_name = random.choice(urls.__all__)
    generator = getattr(urls, generator_name)
    result = await autofill(generator, args=[], memory=memory)
    return result
