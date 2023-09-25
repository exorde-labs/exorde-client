import logging
import argparse

from exorde.models import Processed


from exorde.prepare_batch import prepare_batch
from exorde.process_batch import process_batch, Batch
from exorde.spot_data import spot_data

from exorde.get_transaction_receipt import get_transaction_receipt
from exorde.ipfs import download_ipfs_file, upload_to_ipfs
from exorde.models import LiveConfiguration, StaticConfiguration
from exorde.counter import AsyncItemCounter

import json
import logging
import argparse
import aiohttp
from typing import Callable
from exorde.counter import AsyncItemCounter
from datetime import datetime, timedelta
from uuid import uuid4, UUID

ALIASES_URL: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/domain_aliases.json"


async def _get_alias() -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(ALIASES_URL) as response:
            response.raise_for_status()
            raw_data: str = await response.text()
            try:
                json_data = json.loads(raw_data)
            except Exception:
                logging.exception(raw_data)
                return {
                    "4chan": "4chan",
                    "4channel.org": "4chan",
                    "reddit.com": "reddit",
                    "twitter.com": "twitter",
                    "t.co": "twitter",
                    "x.com": "twitter",
                    "youtube.com": "youtube",
                    "yt.co": "youtube",
                    "mastodon.social": "mastodon",
                    "mastodon": "mastodon",
                    "weibo.com": "weibo",
                    "weibo.org": "weibo",
                    "nostr.social": "nostr",
                    "nostr.com": "forocoches",
                    "jeuxvideo.com": "jvc",
                    "forocoches.com": "forocoches",
                    "bitcointalk.org": "bitcointalk",
                    "ycombinator.com": "hackernews",
                    "tradingview.com": "tradingview",
                    "followin.in": "followin",
                    "seekingalpha.io": "seekingalpha",
                }
            return json_data


def alias_geter() -> Callable:
    memoised = None
    last_call = datetime.now()

    async def get_alias_wrapper() -> dict[str, str]:
        nonlocal memoised, last_call
        now = datetime.now()
        if not memoised or (now - last_call) > timedelta(minutes=1):
            last_call = datetime.now()
            memoised = await _get_alias()
        return memoised

    return get_alias_wrapper


get_aliases = alias_geter()


async def count_rep_for_each_domain(
    counter: AsyncItemCounter, batch: dict
) -> None:
    """
    Uses the Counter in order to store the rep gained for each source. Instead
    of spawning a new specific counter for the task it has been choosed to pre_fix
    each domain with a key `rep_` in order to keep the implementation unique.
    """
    global get_aliases
    aliases = await get_aliases()
    # 1 REP is gained for every new item that has been processed by the protocol
    #   so we have to iterate over the post_upload_file in order to define how
    #   many new items have been processed per source
    for item in batch["items"]:
        domain = item["item"]["domain"]
        alias = aliases.get(domain, "other")
        await counter.increment(f"rep_{alias}")


def generate_spotting_identifier() -> UUID:
    """
    - Spotting identifier are references meant for the web interface.
        - They are used to communicate the state of the spotting job before
            the transaction has been established with the protocol.
        - It allows to follow the progress of the client trough the scope of a
            particular spotting job.
    - (Are NOT equal to the transaction identifier.)
    """
    return uuid4()


def tie_uuid_to_ws_send(uuid: UUID, ws_send: Callable) -> Callable:
    async def identified_websocket_send(state: dict) -> None:
        await ws_send(json.dumps({"jobs": {str(uuid): state}}))

    return identified_websocket_send


async def spotting(
    live_configuration: LiveConfiguration,
    static_configuration: StaticConfiguration,
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
) -> None:
    spotting_identifier: UUID = generate_spotting_identifier()
    identified_websocket_send = tie_uuid_to_ws_send(
        spotting_identifier, websocket_send
    )

    batch: list[tuple[int, Processed]] = await prepare_batch(
        static_configuration,
        live_configuration,
        command_line_arguments,
        counter,
        identified_websocket_send,
        websocket_send,
    )
    try:
        await identified_websocket_send(
            {
                "steps": {
                    "process_batch": {
                        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            }
        )
        logging.info("Processing batch")
        processed_batch: Batch = await process_batch(
            batch, static_configuration
        )
        logging.info("Successfully processed batch")
        await identified_websocket_send(
            {
                "steps": {
                    "process_batch": {
                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            }
        )
    except:
        logging.exception("An error occured during batch processing")
        return
    try:
        await identified_websocket_send(
            {
                "steps": {
                    "ipfs_upload": {
                        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            }
        )
        cid: str = await upload_to_ipfs(processed_batch)
        logging.info("Successfully uploaded file to ipfs")
        post_upload_file: dict = await download_ipfs_file(cid)
        await count_rep_for_each_domain(counter, post_upload_file)
        item_count = len(post_upload_file["items"])
        await identified_websocket_send(
            {
                "steps": {
                    "ipfs_upload": {
                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            }
        )
    except:
        logging.exception("An error occured during IPFS uploading")
        return
    if item_count == 0:
        await identified_websocket_send({"new_items_collected": item_count})
        logging.error(
            "All items of previous batch are already discovered, skipped."
        )
        return
    await identified_websocket_send(
        {
            "steps": {
                "filter": {"end": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            }
        }
    )

    try:
        logging.info(f"Building a spot-data transaction ({item_count} items)")
        transaction_hash, previous_nonce = await spot_data(
            cid,
            item_count,
            static_configuration["worker_account"],
            live_configuration,
            static_configuration["gas_cache"],
            static_configuration["contracts"],
            static_configuration["read_web3"],
            static_configuration["write_web3"],
        )
        await identified_websocket_send({"steps": {"send_spot": "ok"}})
    except:
        logging.exception("An error occured during transaction building")
        return
    try:
        await identified_websocket_send(
            {
                "steps": {
                    "receipt": {
                        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            }
        )

        logging.info("Looking for transaction receipt")
        receipt = await get_transaction_receipt(
            transaction_hash, previous_nonce, static_configuration
        )
        await identified_websocket_send(
            {
                "steps": {
                    "receipt": {
                        "value": str(receipt.blockNumber),
                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                }
            }
        )
        await websocket_send(
            {
                "receipt": {
                    str(spotting_identifier): {
                        "value": str(receipt.blockNumber),
                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                }
            }
        )

    except:
        logging.exception("An error occured during transaction validation")
        return
    logging.info("+ A receipt for previous transaction has been confirmed")
