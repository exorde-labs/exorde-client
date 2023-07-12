import json
import logging
import random
from exorde.get_keywords import get_keywords
from exorde.module_loader import get_scraping_module
import aiohttp
import datetime
from typing import Union
from types import ModuleType


LIVE_PONDERATION = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration.json"
DEV_PONDERATION = "https://gist.githubusercontent.com/6r17/c844775ea359ce10fcc29a72834a5541/raw/3a89b917b2cea609311aefc95f3a46a6cfc066be/gistfile1.txt"
PONDERATION_URL = LIVE_PONDERATION

from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class Ponderation:
    enabled_modules: Dict[str, List[str]]
    generic_modules_parameters: Dict[str, Union[int, str, bool]]
    specific_modules_parameters: Dict[str, Dict[str, Union[int, str, bool]]]
    weights: Dict[str, int]


async def get_ponderation() -> Ponderation:
    async with aiohttp.ClientSession() as session:
        async with session.get(PONDERATION_URL) as response:
            response.raise_for_status()
            raw_data: str = await response.text()
            try:
                json_data = json.loads(raw_data)
            except Exception as error:
                logging.error(raw_data)
                raise error
            enabled_modules = json_data["enabled_modules"]
            generic_modules_parameters = json_data[
                "generic_modules_parameters"
            ]
            specific_modules_parameters = json_data[
                "specific_modules_parameters"
            ]
            weights = json_data["weights"]
            return Ponderation(
                enabled_modules=enabled_modules,
                generic_modules_parameters=generic_modules_parameters,
                specific_modules_parameters=specific_modules_parameters,
                weights=weights,
            )


def ponderation_geter():
    memoised = None
    last_call = datetime.datetime.now()

    async def get_ponderation_wrapper() -> Ponderation:
        nonlocal memoised, last_call
        now = datetime.datetime.now()
        if not memoised or (now - last_call) > datetime.timedelta(minutes=1):
            last_call = datetime.datetime.now()
            memoised = await get_ponderation()
        return memoised

    return get_ponderation_wrapper


get_ponderation = ponderation_geter()


def choose_domain(
    weights: dict[str, int]
) -> str:  # this will return "twitter" "weibo" etc...
    total_weight: int = sum(weights.values())
    choice: float = random.uniform(0, total_weight)
    cumulative_weight: int = 0

    for option, weight in weights.items():
        cumulative_weight += weight
        if choice < cumulative_weight:
            return option

    # This will only execute if the choice exceeds the cumulative weight
    # Return first item if it occurs
    return next(iter(weights))


def choose_module(ponderation: Ponderation) -> str:
    domain = choose_domain(ponderation.weights)
    module_name = ponderation.enabled_modules[domain][0]
    return module_name


async def choose_keyword() -> str:
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


import os


async def think() -> tuple[ModuleType, dict]:
    ponderation: Ponderation = await get_ponderation()
    module: Union[ModuleType, None] = None
    choosen_module: str = ""
    while not module:
        choosen_module = choose_module(ponderation)
        try:
            module = await get_scraping_module(choosen_module)
        except:
            logging.exception(
                f"An error occured loading module {choosen_module}"
            )
            os._exit(-1)
    keyword = await choose_keyword()
    generic_modules_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.generic_modules_parameters
    specific_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.specific_modules_parameters[choosen_module]
    parameters: dict[str, Union[int, str, bool, dict]] = {
        "url_parameters": {"keyword": keyword}
    }
    parameters.update(generic_modules_parameters)
    parameters.update(specific_parameters)
    return (module, parameters)
