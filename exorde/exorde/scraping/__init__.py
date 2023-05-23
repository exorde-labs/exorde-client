from . import urls
from aiosow.bindings import autofill
import random


async def generate_url(memory):
    generator_name = random.choice(dir(urls))
    generator = getattr(urls, generator_name)
    return await autofill(generator, args=[], memory=memory)
