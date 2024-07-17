import asyncio
import json, itertools, logging, aiohttp
from aiohttp import ClientSession
import traceback
from datetime import datetime
from enum import Enum
from typing import Callable, Union

from exorde.create_error_identifier import create_error_identifier


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name  # Serialize Enum value as its name
        return str(super().default(obj))


async def upload_to_ipfs(
    value,
    job_id: str,
    websocket_send: Callable,
    ipfs_path="http://ipfs-api.exorde.network/add",
) -> Union[str, None]:
    empty_content_flag = False
    for i in range(5):  # Retry up to 5 times
        try:
            async with aiohttp.ClientSession() as session:
                _value = json.dumps(
                    value, cls=EnumEncoder
                )  # Make sure EnumEncoder is defined
                async with session.post(
                    ipfs_path,
                    data=_value,
                    headers={"Content-Type": "application/json"},
                    timeout=90,  # Set a timeout for the request
                ) as resp:
                    logging.info(f"[IPFS API Initial trace] Response status = {resp.status}, content = {await resp.text()}")
                    # if empty content in response, raise exception
                    if "empty content" in await resp.text():
                        empty_content_flag = True
                        raise Exception(
                            "[IPFS API] Upload failed because items are too old"
                        )
                    if resp.status == 200:
                        logging.debug("Upload to IPFS succeeded")
                        response = await resp.json()
                        logging.info(
                            f"[IPFS API] Success, response = {response}"
                        )
                        return response["cid"]
                    if resp.status == 500:
                        text = await resp.text()
                        error_identifier = create_error_identifier([text])
                        await websocket_send(
                            {
                                "jobs": {
                                    job_id: {
                                        "steps": {
                                            "ipfs_upload": {
                                                "attempts": {
                                                    i: {
                                                        "status": resp.status,
                                                        "text": text,
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "errors": {
                                    error_identifier: {
                                        "traceback": [text],
                                        "module": "upload_to_ipfs",
                                        "intents": {
                                            job_id: {
                                                datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                ): {}
                                            }
                                        },
                                    }
                                },
                            }
                        )
                        logging.error(
                            f"[IPFS API - Error 500] API rejection: {text}"
                        )
                        if text == "empty content":
                            empty_content_flag = True
                            raise Exception(
                                "[IPFS API] Upload failed because items are too old"
                            )
                        await asyncio.sleep(i * 1.5)  # Adjust sleep factor
                        logging.info(
                            f"Failed upload, retrying ({i + 1}/5)"
                        )  # Update retry count
                        continue  # Retry after handling the error
                    else:
                        error_text = await resp.text()
                        error_identifier = create_error_identifier(
                            [error_text]
                        )
                        await websocket_send(
                            {
                                "jobs": {
                                    job_id: {
                                        "steps": {
                                            "ipfs_upload": {
                                                "attempts": {
                                                    i: {
                                                        "status": resp.status,
                                                        "text": error_text,
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "errors": {
                                    error_identifier: {
                                        "traceback": [error_text],
                                        "module": "upload_to_ipfs",
                                        "intents": {
                                            job_id: {
                                                datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                ): {}
                                            }
                                        },
                                    }
                                },
                            }
                        )

                        logging.info(
                            f"[IPFS API] Failed, response status = {resp.status}, text = {error_text}"
                        )

        except Exception as e:
            if empty_content_flag:
                break
            logging.exception(f"[IPFS API] Error: {e}")
            await asyncio.sleep(i * 1.5)  # Adjust sleep factor
            # Retrieve and format the traceback as a list of strings
            traceback_list = traceback.format_exception(
                type(e), e, e.__traceback__
            )
            error_identifier = create_error_identifier(traceback_list)

            await websocket_send(
                {
                    "jobs": {
                        job_id: {
                            "steps": {
                                "ipfs_upload": {
                                    "attempts": {
                                        i: {
                                            "status": "error",
                                            "error": error_identifier,
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "errors": {
                        error_identifier: {
                            "traceback": traceback_list,
                            "module": "upload_to_ipfs",
                            "intents": {
                                job_id: {
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ): {}
                                }
                            },
                        }
                    },
                }
            )

            logging.info(
                f"Failed upload, retrying ({i + 1}/5)"
            )  # Update retry count

    if empty_content_flag == False:
        await websocket_send(
            {
                "jobs": {
                    job_id: {
                        "steps": {"ipfs_upload": {"failed": "will not retry"}}
                    }
                }
            }
        )

        raise Exception("Failed to upload to IPFS")


def rotate_gateways():
    gateways = [
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        # "https://w3s.link/ipfs/",
        # "https://ipfs.io/ipfs/",
        # "https://ipfs.eth.aragon.network/ipfs/",
        # "https://api.ipfsbrowser.com/ipfs/get.php?hash=",
    ]

    return (gateways[i % len(gateways)] for i in itertools.count())


class DownloadError(Exception):
    pass


async def download_ipfs_file(cid: str, max_attempts: int = 5) -> dict:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
        "Connection": "close",
    }
    gateways = rotate_gateways()

    async with ClientSession(headers=headers) as session:
        for i in range(max_attempts):
            url = next(gateways) + cid
            logging.info("[IPFS Download] download of %s (%s)", url, i)
            try:
                async with session.get(
                    url, timeout=45, allow_redirects=True
                ) as response:
                    if response.status == 200:
                        logging.info("download of %s OK after (%s)", url, i)
                        return await response.json()
                    else:
                        logging.info(
                            "[IPFS Download] Failed download attempt %s of %s, status code: %s",
                            i + 1,
                            max_attempts,
                            response.status,
                        )
            except Exception as error:
                logging.info(
                    "[IPFS Download] Failed to download from %s: %s (%s)",
                    url,
                    error.__class__.__name__,
                    error,
                )
            await asyncio.sleep(i * 1.5)  # Adjust sleep factor

    raise DownloadError(
        "Failed to download file from IPFS after multiple attempts"
    )
