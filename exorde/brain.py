import logging
from importlib import metadata, import_module
import random
from exorde.get_keywords import get_keywords
from exorde.urls import generate_url
from exorde_data import get_scraping_module_for_url
import aiohttp
import datetime
from types import ModuleType


memoised = None
last_call: datetime.datetime = datetime.datetime.now()


async def get_ponderation() -> tuple[list[str], dict[str, float]]:
    global memoised, last_call
    now = datetime.datetime.now()
    if not memoised or (now - last_call) > datetime.timedelta(minutes=1):
        last_call: datetime.datetime = datetime.datetime.now()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration.json"
            ) as response:
                response.raise_for_status()
                json_data: dict = await response.json()
                memoised = json_data
    return (memoised["enabled_modules"], memoised["weights"])


def float_normalization(
    enabled_modules: list[str], weights: dict[str, int]
) -> dict[str, float]:
    total = sum(weights[key] for key in enabled_modules)
    return {key: round(weights[key] / total, 3) for key in enabled_modules}


def choose_value(weights) -> str:
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


async def choose_keyword():
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


async def choose_using_ponderation() -> tuple[str, ModuleType, dict]:
    weights = await get_ponderation()
    choosen_module = choose_value(weights)
    module = import_module(choosen_module)
    keyword = await choose_keyword()
    url = module.generate_url(keyword)
    parameters = {}
    return (url, module, parameters)


async def choose_randomly() -> tuple[str, ModuleType, dict]:
    selected_keyword = await choose_keyword()
    logging.info(f"[BRAIN] Selected Keyword : {selected_keyword}")
    url = await generate_url(selected_keyword)
    module = await get_scraping_module_for_url(url)
    logging.info(f"[BRAIN] Selected URL : {url}")
    logging.info(
        f"[BRAIN] Selected Module : {module.__name__} ({metadata.version(module.__name__)})"
    )
    parameters = {}
    return url, module, parameters


think = choose_randomly
