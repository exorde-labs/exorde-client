import os
import json
import logging
import random
import argparse
from exorde.get_keywords import get_keywords
from exorde.module_loader import get_scraping_module
import aiohttp
from typing import Union, Callable
from types import ModuleType
from datetime import datetime, timedelta
from exorde.counter import AsyncItemCounter

LIVE_PONDERATION: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration.json"
DEV_PONDERATION: str = "https://gist.githubusercontent.com/6r17/c844775ea359ce10fcc29a72834a5541/raw/6e615a180946dbc1eb6c0046045c82decd22a0e3/gistfile1.txt"
PONDERATION_URL: str = DEV_PONDERATION

from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class Ponderation:
    enabled_modules: Dict[str, List[str]]
    generic_modules_parameters: Dict[str, Union[int, str, bool]]
    specific_modules_parameters: Dict[str, Dict[str, Union[int, str, bool]]]
    weights: Dict[str, float]


async def _get_ponderation() -> Ponderation:
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


def ponderation_geter() -> Callable:
    memoised = None
    last_call = datetime.now()

    async def get_ponderation_wrapper() -> Ponderation:
        nonlocal memoised, last_call
        now = datetime.now()
        if not memoised or (now - last_call) > timedelta(minutes=1):
            last_call = datetime.now()
            memoised = await _get_ponderation()
        return memoised

    return get_ponderation_wrapper


get_ponderation: Callable = ponderation_geter()

from exorde.weighted_choice import weighted_choice


async def generate_quota_layer(
    command_line_arguments: argparse.Namespace, counter: AsyncItemCounter
) -> dict[str, float]:
    quotas = {k: v for d in command_line_arguments.quota for k, v in d.items()}
    counts = {
        k: await counter.count_occurrences(k) for k, __v__ in quotas.items()
    }
    layer = {
        k: 1.0 if counts[k] < quotas[k] else 0.0 for k, __v__ in quotas.items()
    }
    return layer


async def generate_only_layer(
    weights: dict[str, float],
    command_line_arguments: argparse.Namespace,
) -> dict[str, float]:
    onlies: list[str] = command_line_arguments.only.split(",")
    if onlies == [""]:
        return {}
    return {k: 1.0 if k in onlies else 0.0 for k, __v__ in weights.items()}


async def choose_domain(
    weights: dict[str, float],
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
) -> str:  # this will return "twitter" "weibo" etc...
    quota_layer = await generate_quota_layer(command_line_arguments, counter)
    only_layer = await generate_only_layer(weights, command_line_arguments)
    matrix: list[dict[str, float]] = [weights, quota_layer, only_layer]
    return weighted_choice(matrix)


def get_module_path_for_domain(ponderation: Ponderation, domain: str) -> str:
    module_path = ponderation.enabled_modules[domain][0]
    return module_path


async def choose_keyword() -> str:
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


async def print_counts(ponderation: dict[str, float], counter):
    for item in ponderation:
        twenty_four = await counter.count_occurrences(item)
        one = await counter.count_occurrences(
            item, time_period=timedelta(hours=1)
        )
        logging.info(
            f"{item} : {twenty_four} last 24h | {one} last hour | {counter.count(item)} since software launch"
        )
    logging.info("")


async def think(
    command_line_arguments: argparse.Namespace, counter: AsyncItemCounter
) -> tuple[ModuleType, dict, str]:
    ponderation: Ponderation = await get_ponderation()
    await print_counts(ponderation.weights, counter)
    module: Union[ModuleType, None] = None
    choosen_module: str = ""
    user_module_overwrite: dict[str, str] = {
        option.split("=")[0]: option.split("=")[1]
        for option in command_line_arguments.module_overwrite
    }
    domain: str = ""
    while not module:
        domain = await choose_domain(
            ponderation.weights, command_line_arguments, counter
        )
        if domain in user_module_overwrite:
            logging.info("{domain} overloaded by user")
            choosen_module_path: str = user_module_overwrite[domain]
        else:
            choosen_module_path: str = get_module_path_for_domain(
                ponderation, domain
            )
        try:
            module = await get_scraping_module(choosen_module_path)
        except:
            logging.exception(
                f"An error occured loading module {choosen_module}"
            )
            os._exit(-1)

    keyword: str = await choose_keyword()
    generic_modules_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.generic_modules_parameters
    specific_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.specific_modules_parameters.get(choosen_module, {})
    parameters: dict[str, Union[int, str, bool, dict]] = {
        "url_parameters": {"keyword": keyword},
        "keyword": keyword,
    }
    parameters.update(generic_modules_parameters)

    parameters.update(specific_parameters)
    return (module, parameters, domain)
