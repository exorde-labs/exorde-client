import logging
import argparse
import os
from exorde.models import Processed

from typing import Union
from exorde.prepare_batch import prepare_batch
from exorde.process_batch import process_batch, Batch

from exorde.ipfs import EnumEncoder
from exorde.models import LiveConfiguration, StaticConfiguration
from exorde.counter import AsyncItemCounter

import json
import os
import hashlib
import random
import string
import json
import logging
import argparse
import aiohttp
from typing import Callable
from exorde.counter import AsyncItemCounter
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from exorde.create_error_identifier import create_error_identifier
import traceback

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
                    "threads.net":"threads",
                    "bsky.app":"bluesky",
                    "bsky.social":"bluesky",
                    "bluesky.social":"bluesky"                    
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


def save_json_to_file(data, folder_path='output_folder'):
    """Save JSON data to a file with a random hash filename in the specified folder."""
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Generate a random hash for the filename
    filename = f"{generate_random_hash()}.json"
    file_path = os.path.join(folder_path, filename)
    
    # Write JSON data to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4, cls=EnumEncoder)
    
    return file_path

async def spotting(
    live_configuration: LiveConfiguration,
    static_configuration: StaticConfiguration,
    command_line_arguments: argparse.Namespace,
    counter: AsyncItemCounter,
    websocket_send: Callable,
) -> None:
    spotting_identifier: str = str(uuid4())
    await websocket_send(
        {
            "jobs": {
                spotting_identifier: {
                    "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

    batch: list[tuple[int, Processed]] = await prepare_batch(
        static_configuration,
        live_configuration,
        command_line_arguments,
        counter,
        websocket_send,
        spotting_identifier,
    )
    await websocket_send(
        {
            "jobs": {
                spotting_identifier: {
                    "steps": {
                        "process_batch": {
                            "start": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        }
                    }
                }
            }
        }
    )
    logging.info("Processing batch")
    try:
        processed_batch: Batch = await process_batch(
            batch, static_configuration
        )
        logging.info("Successfully processed batch")
        ###############################################
        ###   SETTING HUGGINFACE HUB TO OFFLINE MODE
        ##### NOW THAT ALL MODELS ARE PROVEN OK
        # check if TRANSFORMERS_OFFLINE env var is 0
        # if so, set it to 1 and print the change

        # Check if the TRANSFORMERS_OFFLINE environment variable is set and not equal to '1'
        if os.environ.get("TRANSFORMERS_OFFLINE") != "1":
            # Set the TRANSFORMERS_OFFLINE environment variable to '1'
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            logging.info("TRANSFORMERS_OFFLINE environment variable was set to 1.")
        else:
            # If the variable is already set to '1', inform the user
            logging.info("[HUGGING FACE MODE] OFFLINE")

        ###############################################
        await websocket_send(
            {
                "jobs": {
                    spotting_identifier: {
                        "steps": {
                            "process_batch": {
                                "end": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            }
                        }
                    }
                }
            }
        )
    except Exception as e:
        traceback_list = traceback.format_exception(
            type(e), e, e.__traceback__
        )
        error_id = create_error_identifier(traceback_list)

        await websocket_send(
            {
                "jobs": {
                    spotting_identifier: {
                        "steps": {
                            "process_batch": {
                                "end": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "failed": "will not retry",
                            }
                        }
                    }
                },
                "errors": {
                    error_id: {
                        "traceback": traceback_list,
                        "module": "process",
                        "intents": {
                            spotting_identifier: {
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ): {}
                            }
                        },
                    }
                },
            }
        )
        logging.exception("An error occured during batch processing")
        return
    # HTTP POST submission (replaces IPFS + blockchain)
    try:
        await websocket_send(
            {
                "jobs": {
                    spotting_identifier: {
                        "steps": {
                            "http_submit": {
                                "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                    }
                }
            }
        )
        
        # Serialize processed_batch as-is (same as upload_to_ipfs did)
        batch_json = json.dumps(processed_batch, cls=EnumEncoder)
        batch_dict = json.loads(batch_json)  # Parse once for both uses
        
        # Get MAIN_ADDRESS from command line args
        main_address = command_line_arguments.main_address
        
        # Create FormData with file field (API expects multipart/form-data)
        form = aiohttp.FormData()
        form.add_field('file', batch_json, 
                       filename=f'batch_{spotting_identifier}.json',
                       content_type='application/json')
        
        # POST to API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://upload.exorde.network/v1/upload",
                data=form,
                headers={"MAIN_ADDRESS": main_address},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    
                    # Log full API response
                    logging.info(f"[API Response] {json.dumps(response_data, indent=2)}")
                    
                    # Extract metrics
                    total_items = response_data.get("total_items", 0)
                    filtered_items = response_data.get("filtered_items", 0)
                    rejected_items = response_data.get("rejected_items", 0)
                    duplicate_items = response_data.get("duplicate_items", 0)
                    file_id = response_data.get("file_id", "unknown")
                    processing_ms = response_data.get("processing_time_ms", 0)
                    
                    # Calculate submitted count
                    submitted_count = len(batch_dict.get("items", []))
                    
                    # Detailed logging
                    logging.info(
                        f"✅ Batch uploaded successfully:\n"
                        f"  File ID: {file_id}\n"
                        f"  Submitted: {submitted_count} items\n"
                        f"  Total processed: {total_items} items\n"
                        f"  Accepted (filtered): {filtered_items} items\n"
                        f"  Rejected: {rejected_items} items\n"
                        f"  Duplicates: {duplicate_items} items\n"
                        f"  API processing time: {processing_ms}ms"
                    )
                    
                    # Count rep for each domain using filtered items
                    await count_rep_for_each_domain(counter, batch_dict)
                    
                    await websocket_send({
                        "jobs": {
                            spotting_identifier: {
                                "steps": {
                                    "http_submit": {
                                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "submitted": submitted_count,
                                        "accepted": filtered_items,
                                        "rejected": rejected_items,
                                        "duplicates": duplicate_items,
                                        "file_id": file_id
                                    }
                                },
                                "new_items_collected": filtered_items  # Use filtered count
                            }
                        }
                    })
                    
                else:
                    error_text = await resp.text()
                    logging.error(f"❌ API submission failed: HTTP {resp.status}\n{error_text}")
                    await websocket_send({
                        "jobs": {
                            spotting_identifier: {
                                "steps": {
                                    "http_submit": {
                                        "failed": f"status_{resp.status}",
                                        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                }
                            }
                        }
                    })
                    return
    
    except Exception as e:
        logging.exception("An error occurred during HTTP submission")
        traceback_list = traceback.format_exception(type(e), e, e.__traceback__)
        error_id = create_error_identifier(traceback_list)
        
        await websocket_send({
            "jobs": {
                spotting_identifier: {
                    "steps": {
                        "http_submit": {
                            "failed": error_id,
                            "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                }
            },
            "errors": {
                error_id: {
                    "traceback": traceback_list,
                    "module": "http_submit"
                }
            }
        })
        return
    
    logging.info("+ Batch submitted successfully via HTTP POST")
