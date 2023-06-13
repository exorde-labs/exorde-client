import aiohttp, os, subprocess
from importlib import metadata

from get_latest_tag import get_latest_tag


async def self_update():
    latest_tag = await get_latest_tag()
    local_version = metadata.version("exorde")
    if latest_tag != local_version:
        subprocess.check_call(
            [
                "pip",
                "install",
                "https://github.com/exorde-labs/exorde",
            ]
        )
        os._exit(0)
