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
DEV_PONDERATION = "https://gist.githubusercontent.com/6r17/082bb252f504f80610602b0288baffd6/raw/0ad0b1f720f1ad1e6ce28da53e1550c4f7c146cd/ponderation.json"
PONDERATION = LIVE_PONDERATION


def ponderation_geter():
    memoised = None
    last_call = datetime.datetime.now()

    async def get_ponderation() -> tuple[list[str], dict, dict[str, float]]:
        nonlocal memoised, last_call
        now = datetime.datetime.now()
        if not memoised or (now - last_call) > datetime.timedelta(minutes=1):
            last_call = datetime.datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(PONDERATION) as response:
                    response.raise_for_status()
                    raw_data: str = await response.text()
                    try:
                        json_data = json.loads(raw_data)
                    except Exception as error:
                        logging.error(raw_data)
                        raise error
                    memoised = json_data
        return (
            memoised["enabled_modules"],
            memoised["parameters"],
            memoised["weights"],
        )

    return get_ponderation


get_ponderation = ponderation_geter()


def choose_value(weights) -> str:
    print(weights)
    total_weight: int = sum(weights.values())
    choice: float = random.uniform(0, total_weight)
    cumulative_weight: int = 0

    for option, weight in weights.items():
        cumulative_weight += weight
        if choice < cumulative_weight:
            return option

    # This will only execute if the choice exceeds the cumulative weight
    # Return first item if it occurs
    return weights.items()[0][0]


async def choose_keyword() -> str:
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


async def think() -> tuple[ModuleType, dict]:
    __enabled_modules__, _parameters, weights = await get_ponderation()
    module: Union[ModuleType, None] = None
    choosen_module: str = ""
    while not module:
        choosen_module = choose_value(weights)
        try:
            module = await get_scraping_module(choosen_module)
        except:
            logging.exception(
                f"An error occured loading module {choosen_module}"
            )
    keyword = await choose_keyword()
    common_parameters = _parameters["common_parameters"]
    specific_parameters = _parameters["specific_parameters"][choosen_module]
    parameters: dict[str, dict] = {"url_parameters": {"keyword": keyword}}
    parameters.update(common_parameters)
    parameters.update(specific_parameters)
    return (module, parameters)
