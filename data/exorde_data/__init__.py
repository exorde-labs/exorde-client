import logging
from typing import AsyncGenerator
import json
from importlib import metadata
from exorde_data.models import *
from madtypes import json_schema

from . import scraping


def install_modules():
    raise NotImplementedError("Module installation is not implemented")


def get_scraping_module(url: str):
    for module_name in dir(scraping):
        if module_name in url:
            return getattr(scraping, module_name)
    return None


from typing import Union


async def query(url: str) -> AsyncGenerator[Union[Item, None], None]:
    scraping_module = get_scraping_module(url)
    if not scraping_module:
        logging.debug(f"Installed modules are : {dir(scraping)}")
        raise NotImplementedError(f"There is no scraping module for {url}")
    try:
        generator = scraping_module.query(url)
        async for item in generator:
            yield item
    except:
        yield None


def print_schema():
    schem = json_schema(
        Item,
        **{
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f'https://github.com/exorde-labs/exorde/repo/tree/v{metadata.version("exorde_data")}/exorde/schema/schema.json',
        },
    )
    try:
        print(
            json.dumps(
                schem,
                indent=4,
            )
        )
    except Exception as err:
        print(err)
        print(schem)


__all__ = ["scraping"]
