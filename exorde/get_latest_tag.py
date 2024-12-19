import aiohttp
import logging
import os

async def get_latest_tag():
    logging.info("GET_LATEST_TAG")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/repos/exorde-labs/exorde-client/releases/latest"
        ) as response:
            body = await response.json()
            try:
                return body["tag_name"]
            except:
                logging.info(body)
                os._exit(-1)
