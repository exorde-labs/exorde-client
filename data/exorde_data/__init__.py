from typing import AsyncGenerator
import json
from importlib import metadata
from exorde_data.models import Item

from . import scraping


def install_modules():
    raise NotImplemented()


def get_scraping_module(url: str):
    for module_name in dir(scraping):
        if module_name in url:
            return getattr(scraping, module_name)
    return None


async def query(url: str) -> AsyncGenerator[Item, None]:
    scraping_module = get_scraping_module(url)
    if not scraping_module:
        raise NotImplemented(f"There is no scraping module for {url}")
    async for item in scraping_module.query(url):
        yield item


def print_schema():
    print(
        json.dumps(
            Item().json_schema(
                **{
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "$id": f'https://github.com/exorde-labs/exorde/repo/tree/v{metadata.version("exorde_data")}/exorde/schema/schema.json',
                }
            ),
            indent=4,
        )
    )


__all__ = ["scraping"]
