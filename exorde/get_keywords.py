import logging, os, json, aiohttp, time, re, random, asyncio, traceback
from datetime import datetime

from exorde.models import Ponderation

FALLBACK_DEFAULT_LIST = [
    "bitcoin",
    "ethereum",
    "eth",
    "btc",
    "usdt",
    "usdc",
    "stablecoin",
    "defi",
    "finance",
    "liquidity",
    "token",
    "economy",
    "markets",
    "stocks",
    "crisis",
]
KEYWORDS_URL = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/keywords.txt"
JSON_FILE_PATH = "keywords.json"
KEYWORDS_UPDATE_INTERVAL = 5 * 60  # 5 minutes


## READ KEYWORDS FROM SOURCE OF TRUTH
async def fetch_keywords(keywords_raw_url) -> str:
    for i in range(0, 10):
        await asyncio.sleep(i * i)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    keywords_raw_url, timeout=10
                ) as response:
                    return await response.text()
        except Exception as e:
            logging.info(
                "[KEYWORDS] Failed to download keywords.txt from Github repo exorde-labs/TestnetProtocol: %s",
                e,
            )
    raise ValueError(
        "[KEYWORDS] Failed to download keywords.txt from Github repo exorde-labs/TestnetProtocol: %s"
    )


## CACHING MECHANISM
# save keywords to a local file, at root directory, alongside the timestamp of the update
def save_keywords_to_json(keywords):
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as json_file:
        json.dump(
            {"last_update_ts": int(time.time()), "keywords": keywords},
            json_file,
            ensure_ascii=False,
        )


# load keywords from local file, if exists
def load_keywords_from_json():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return data["keywords"]
    return None


#######################################################################################################
def filter_strings(str_list):
    # Step 1: strip each string and remove '\n', '\r' characters
    step1 = [s.strip().replace("\n", "").replace("\r", "") for s in str_list]
    # Step 2: remove '\\uXXXX' characters
    step2 = [re.sub(r"\\u[\da-fA-F]{4}", "", s) for s in step1]
    step3 = [s for s in step2 if s]

    return step3


#######################################################################################################
async def get_keywords():
    # Checking if JSON file exists.
    if os.path.exists(JSON_FILE_PATH):
        try:
            # Attempting to read the JSON file.
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                last_update_ts = data.get("last_update_ts", 0)
                ts = int(time.time())
                # If last update was less than 5 minutes ago, return the stored keywords
                if ts - last_update_ts < KEYWORDS_UPDATE_INTERVAL:
                    return data.get("keywords", [])
        except Exception as e:
            logging.info(f"[KEYWORDS] Error during reading the JSON file: {e}")

    # If execution reaches here, it means either JSON file does not exist
    # or the last update was more than 5 minutes ago. So, we attempt to fetch the keywords from the URL.
    try:
        keywords_txt = await fetch_keywords(KEYWORDS_URL)

        # Checking if fetch_keywords returned None.
        if keywords_txt is None:
            raise Exception("fetch_keywords returned None")

        keywords = keywords_txt.replace("\n", "").split(",")
        keywords = filter_strings(keywords)
        save_keywords_to_json(keywords)
        return keywords
    except Exception as e:
        logging.info(
            f"[KEYWORDS] Error during the processing of the keywords list: {e}"
        )

    # If execution reaches here, it means either fetch_keywords returned None
    # or there was an error during processing the keywords. Attempt to return the keywords from the JSON file, if it exists.
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                return data.get("keywords", [])
        except Exception as e:
            logging.info(f"[KEYWORDS] Error during reading the JSON file: {e}")
    # If execution reaches here, it means either JSON file does not exist
    # or there was an error during reading the JSON file.
    # Return the fallback default list.
    logging.info(f"[KEYWORDS] Returning default fallback list")
    return FALLBACK_DEFAULT_LIST


from typing import Optional, Dict, Union, Callable


def create_topic_lang_fetcher(refresh_frequency: int = 3600):
    url: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/topic_lang_keywords.json"
    cached_data: Optional[Dict[str, list[str]]] = None
    last_fetch_time: float = 0

    async def fetch_data() -> dict[str, dict[str, list[str]]]:
        nonlocal cached_data, last_fetch_time
        current_time: float = time.time()

        # Check if data should be refreshed
        if (
            cached_data is None
            or current_time - last_fetch_time >= refresh_frequency
        ):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        data = json.loads(await response.text())
                        cached_data = data
                        last_fetch_time = current_time
                        logging.info(
                            "Data refreshed at: %s",
                            time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime()
                            ),
                        )
            except Exception as e:
                logging.error("Error fetching data: %s", str(e))
        if not cached_data:
            raise Exception("Could not download topics")
        else:
            return cached_data

    return fetch_data


topic_lang_fetcher = create_topic_lang_fetcher()

import os
import itertools


async def new_choose_keyword(
    module_name: str,
    module_configuration: Ponderation,
    websocket_send: Callable,
    intent_id: str,
):
    """New keyword_choose alg takes into account the module language"""
    module_languages = module_configuration.lang_map[module_name]

    topic_lang: dict[str, dict[str, list[str]]] = await topic_lang_fetcher()
    topics: list[str] = list(topic_lang.keys())
    choosed_topic = random.choice(topics)
    try:
        choosed_language = random.choice(module_languages)

        await websocket_send(
            {
                "intents": {
                    intent_id: {
                        "lang": choosed_language,
                        "topic": choosed_topic,
                    }
                }
            }
        )

        if choosed_language == "all":
            topic_data: dict[str, list[str]] = topic_lang[choosed_topic]
            all_keywords_lists = [
                topic_data[language] for language in topic_data
            ]
            merged_keywords = list(itertools.chain(*all_keywords_lists))
            return random.choice(merged_keywords)
        else:
            translated_keyword = choosed_topic[choosed_language]
        return translated_keyword
    except:
        return choosed_topic


async def default_choose_keyword():
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


from exorde.create_error_identifier import create_error_identifier


async def choose_keyword(
    module_name: str,
    module_configuration: Ponderation,
    websocket_send: Callable,
    intent_id: str,
) -> str:
    algorithm_choose_cursor = module_configuration.new_keyword_alg
    random_number = random.randint(0, 99)
    if random_number <= algorithm_choose_cursor:
        try:
            await websocket_send(
                {
                    "intents": {
                        intent_id: {
                            "keyword_alg": "new",
                            "cursor": algorithm_choose_cursor,
                            "number": random_number,
                        }
                    }
                }
            )
            return await new_choose_keyword(
                module_name, module_configuration, websocket_send, intent_id
            )
        except Exception as e:
            traceback_list = traceback.format_exception(
                type(e), e, e.__traceback__
            )
            error_id = create_error_identifier(traceback_list)

            await websocket_send(
                {
                    "intents": {
                        intent_id: {
                            "keyword_alg": "old",
                            "cursor": algorithm_choose_cursor,
                            "number": random_number,
                            "error": error_id,
                        }
                    },
                    "errors": {
                        error_id: {
                            "traceback": traceback_list,
                            "module": "get_keywords",
                            "intents": {
                                intent_id: {
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ): {}
                                }
                            },
                        }
                    },
                }
            )
            return await default_choose_keyword()
    await websocket_send(
        {
            "intents": {
                intent_id: {
                    "keyword_alg": "old",
                    "cursor": algorithm_choose_cursor,
                    "number": random_number,
                }
            }
        }
    )

    return await default_choose_keyword()
