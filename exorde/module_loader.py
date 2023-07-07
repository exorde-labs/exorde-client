import subprocess
from importlib import metadata
from importlib import import_module, metadata
import re
import aiohttp
import subprocess
from types import ModuleType


from importlib.metadata import PackageNotFoundError


import os


async def is_up_to_date(repository_path) -> bool:
    async def fetch_version_from_setup_file(setup_file_url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(setup_file_url) as response:
                # Error handling for non-successful HTTP status codes
                if response.status != 200:
                    raise ValueError(
                        "An error occured while fetching the setup file at specified endpoint"
                    )

                # Asynchronously read response data
                response_text = await response.text()

                # Use regular expressions to parse setup version
                version_match = re.search(r'version="(.+?)"', response_text)
                if version_match:
                    return version_match.group(1)
                else:
                    raise ValueError(
                        "No version were found in the specified setup file"
                    )

    try:
        module_name = os.path.basename(repository_path.rstrip("/"))
    except:
        raise TypeError(
            f"is_up_to_date(repository_path), '{repository_path}' is not a valid repository"
        )
    try:
        local_version = metadata.version(module_name)
    except PackageNotFoundError:
        return False

    online_version = await fetch_version_from_setup_file(repository_path)

    return True


async def get_scraping_module(repository_path) -> ModuleType:
    module_name = os.path.basename(repository_path.rstrip("/"))
    if not is_up_to_date(repository_path):
        subprocess.check_call(["pip", "install", module_name])
    loaded_module = import_module(module_name)
    return loaded_module
