import os
import json
import logging
import argparse
from exorde.get_keywords import choose_keyword
from exorde.module_loader import get_scraping_module
import aiohttp
import datetime
from typing import Union, Callable
from types import ModuleType
from exorde.counter import AsyncItemCounter
from datetime import datetime, timedelta, time
from exorde.at import at
from datetime import timedelta
import logging


from exorde.at import at
from datetime import timedelta
import logging


from exorde.statistics_notification import statistics_notification

LIVE_PONDERATION: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration_v2.json"
DEV_PONDERATION: str = "https://gist.githubusercontent.com/MathiasExorde/179ce30c736d1e3af924a767fadd2088/raw/d16444bc06cb4028f95647dafb6d55ee201fd8c6/new_module_configuration.json"
PONDERATION_URL: str = LIVE_PONDERATION

from typing import Union
from exorde.models import Ponderation


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
                lang_map=json_data["lang_map"],
                new_keyword_alg=json_data["new_keyword_alg"],
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
    weights: dict[str, float], quota_layer, only_layer
) -> str:  # this will return "twitter" "weibo" etc...
    matrix: list[dict[str, float]] = [weights, quota_layer, only_layer]
    return weighted_choice(matrix)


def get_module_path_for_domain(ponderation: Ponderation, domain: str) -> str:
    module_path = ponderation.enabled_modules[domain][0]
    return module_path


def deep_merge_dict(dict1, dict2):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2

    merged = dict1.copy()
    for key, value2 in dict2.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value2, dict)
        ):
            merged[key] = deep_merge_dict(merged[key], value2)
        else:
            merged[key] = value2

    return merged


async def print_counts(
    ponderation: Ponderation,
    counter: AsyncItemCounter,
    quota_layer: dict[str, float],
    only_layer: dict[str, float],
    websocket_send: Callable,
):
    weights: dict[str, float] = ponderation.weights
    # Find the length of the longest item in ponderation
    max_length = max(len(item) for item in weights)
    max_count_length = 10  # Fixed width for the count columns

    # Get the counts for the last 30 items
    last_30_items_counts = await counter.count_last_n_items(30)

    logging.info(
        f"{'     source':>{max_length}} | {'weights':>{max_count_length}} | {'quota':>{max_count_length}} | {'only':>{max_count_length}} | {'last 24 h':>{max_count_length}} | {'last 1 h':>{max_count_length}} | {'last 30 items':>{max_count_length}} | {'REP':>{max_count_length}}"
    )
    logging.info(
        "-"
        * (
            max_length + 6 * max_count_length + 15
        )  # 15 includes spaces, vertical bars, and other characters
    )
    total_earned_reputation: int = 0
    update = {}
    for item in weights:
        count_twenty_four = await counter.count_occurrences(item)
        count_one_hour = await counter.count_occurrences(
            item, time_period=timedelta(hours=1)
        )
        count_last_30_items = last_30_items_counts.get(item, 0)
        weight_value = weights.get(item, 0)
        quota_value = quota_layer.get(item, 0)
        only_value = only_layer.get(item, 0)
        rep_value = await counter.count_occurrences(
            "rep_" + item
        )  # / ! \ this will show the REP gained on last 24hours
        # Use string formatting to right-align all columns
        update = deep_merge_dict(
            update,
            {
                "statistics": {
                    item: {
                        "24": count_twenty_four,
                        "1": count_one_hour,
                        "30": count_last_30_items,
                        "rep": rep_value,
                    }
                }
            },
        )

        logging.info(
            f"   {item:>{max_length}} | {weight_value:>{max_count_length}} | {quota_value:>{max_count_length}} | {only_value:>{max_count_length}} | {count_twenty_four:>{max_count_length}} | {count_one_hour:>{max_count_length}} | {count_last_30_items:>{max_count_length}} | {rep_value:>{max_count_length}}"
        )
    item = "other"
    count_twenty_four = await counter.count_occurrences(item)
    count_one_hour = await counter.count_occurrences(
        item, time_period=timedelta(hours=1)
    )
    count_last_30_items = last_30_items_counts.get(item, 0)
    weight_value = weights.get(item, 0)
    quota_value = quota_layer.get(item, 0)
    only_value = only_layer.get(item, 0)
    rep_value = await counter.count_occurrences(
        "rep_" + item
    )  # / ! \ this will show the REP gained on last 24hours
    # Use string formatting to right-align all columns
    update = deep_merge_dict(
        update,
        {
            "statistics": {
                "other": {
                    "24": count_twenty_four,
                    "1": count_one_hour,
                    "30": count_last_30_items,
                    "rep": rep_value,
                }
            }
        },
    )
    await websocket_send(update)
    logging.info(
        f"   {item:>{max_length}} | {weight_value:>{max_count_length}} | {quota_value:>{max_count_length}} | {only_value:>{max_count_length}} | {count_twenty_four:>{max_count_length}} | {count_one_hour:>{max_count_length}} | {count_last_30_items:>{max_count_length}} | {rep_value:>{max_count_length}}"
    )

    logging.info("")


import asyncio


async def think(
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
    intent_id: str,
) -> tuple[ModuleType, dict, str]:
    ponderation: Ponderation = await get_ponderation()  # module_configuration
    quota_layer: dict[str, float] = await generate_quota_layer(
        command_line_arguments, counter
    )
    only_layer: dict[str, float] = await generate_only_layer(
        ponderation.weights, command_line_arguments
    )
    tasks = asyncio.all_tasks()
    await websocket_send(
        {
            "quota": quota_layer,
            "only": only_layer,
            "weights": ponderation.weights,
            "tasks": str(list(tasks)[0].get_stack()),
        }
    )
    await print_counts(
        ponderation, counter, quota_layer, only_layer, websocket_send
    )

    croned_statistics_notification = at(
        [time(hour, 0) for hour in command_line_arguments.notify_at],
        "/tmp/exorde/statistics_notifications.json",
        statistics_notification,
    )
    await croned_statistics_notification(
        ponderation, counter, quota_layer, only_layer, command_line_arguments
    )
    module: Union[ModuleType, None] = None
    choosen_module_path: str = ""
    user_module_overwrite: dict[str, str] = {
        option.split("=")[0]: option.split("=")[1]
        for option in command_line_arguments.module_overwrite
    }
    domain: str = ""
    remaining_iterations_looping = 200
    while not module:
        domain = await choose_domain(
            ponderation.weights, quota_layer, only_layer
        )
        if domain in user_module_overwrite:
            logging.info("{domain} overloaded by user")
            choosen_module_path: str = user_module_overwrite[domain]
        else:
            choosen_module_path: str = get_module_path_for_domain(
                ponderation, domain
            )
        try:
            module = await get_scraping_module(
                choosen_module_path, websocket_send
            )
        except:
            logging.exception(
                f"An error occured loading module {choosen_module_path}"
            )
            os._exit(-1)
        ## loop safe guard
        remaining_iterations_looping -= 1
        if remaining_iterations_looping <= 0:
            break

    keyword: str = await choose_keyword(
        module.__name__, ponderation, websocket_send, intent_id
    )
    generic_modules_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.generic_modules_parameters
    specific_parameters: dict[
        str, Union[int, str, bool, dict]
    ] = ponderation.specific_modules_parameters.get(choosen_module_path, {})
    parameters: dict[str, Union[int, str, bool, dict]] = {
        "url_parameters": {"keyword": keyword},
        "keyword": keyword,
    }
    parameters.update(generic_modules_parameters)
    parameters.update(specific_parameters)
    return (module, parameters, domain)
