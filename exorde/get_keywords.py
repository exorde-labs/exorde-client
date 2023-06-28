import logging, os, json, aiohttp, time, re

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
async def fetch_keywords(keywords_raw_url) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(keywords_raw_url, timeout=10) as response:
                return await response.text()
    except Exception as e:
        logging.info(
            "[KEYWORDS] Failed to download keywords.txt from Github repo exorde-labs/TestnetProtocol: %s",
            e,
        )
        return None


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
