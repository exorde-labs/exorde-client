import logging
from typing import AsyncGenerator
import json
from importlib import metadata
from exorde_data.models import *
from madtypes import json_schema
from importlib import import_module, metadata
import re
import aiohttp
from typing import Union


def install_modules():
    raise NotImplementedError("Module installation is not implemented")


async def fetch_version_from_setup_file(url_endpoint: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url_endpoint) as response:
            # Error handling for non-successful HTTP status codes
            if response.status != 200:
                raise ValueError(
                    "An error occured while fetching the setup file at specified endpoint"
                )

            # Asynchronously read response data
            response_text = await response.text()

            # Use regular expressions to parse setup version
            version_match = re.search(r'version="(.+?)"', response_text)
            if version_match:
                return version_match.group(1)
            else:
                raise ValueError(
                    "No version were found in the specified setup file"
                )


async def get_module_online_version(module_name: str):
    repository_path = f"https://raw.githubusercontent.com/exorde-labs/exorde/selfupdate/data/scraping/{module_name}"
    return await fetch_version_from_setup_file(f"{repository_path}/setup.py")


import subprocess


async def get_scraping_module(module_name):
    from exorde_data.scraping import scraping_modules

    module_hash = scraping_modules[module_name]
    module_version = metadata.version(module_hash)
    online_module_version = await get_module_online_version(module_name)
    if module_version != online_module_version:
        logging.info(
            "diff in versions : {module_version} != {online_module_version}"
        )
        repository_path = f"https://github.com/exorde-labs/exorde/tree/selfupdate/data/scraping/{module_name}"
        subprocess.check_call(["pip", "install", repository_path])
    loaded_module = import_module(module_hash)
    return loaded_module


async def get_scraping_module_name_from_url(
    url: str, self_update: bool = False
):
    mapping_url = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/selfupdate/targets/scraping_module_substrings_mapping.json"

    # If self_update is True, fetch the latest mapping from the GitHub URL
    if self_update:
        async with aiohttp.ClientSession() as session:
            async with session.get(mapping_url) as resp:
                if resp.status != 200:
                    print(f"Unable to fetch data: HTTP {resp.status}")
                    return None

                data = await resp.text()
                mapping = json.loads(data)
    else:
        # Define an initial static mapping here if self_update is False
        mapping = {
            "4chan": ["4chan", "4channel"],
            "reddit": ["reddit.com"],
            "twitter": ["twitter.com", "t.co"],
        }

    # Check each module in the mapping for substring matches
    for module, substrings in mapping.items():
        for substring in substrings:
            if substring in url:
                return module

    raise ValueError("No key for provided url")


async def get_scraping_module_for_url(url: str, self_update: bool = False):
    name = await get_scraping_module_name_from_url(
        url, self_update=self_update
    )
    return await get_scraping_module(name)


async def query(
    url: str, self_update: bool = False
) -> AsyncGenerator[Union[Item, None], None]:
    scraping_module = await get_scraping_module_for_url(
        url, self_update=self_update
    )
    if not scraping_module:
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
