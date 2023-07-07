import subprocess
import logging
from importlib import metadata
from importlib import import_module, metadata
import re
import aiohttp
import subprocess
from types import ModuleType


from importlib.metadata import PackageNotFoundError


import os


async def is_up_to_date(repository_path) -> bool:
    def is_older_version(version1, version2):
        # Remove the "v" prefix if present
        if version1.startswith("v"):
            version1 = version1[1:]
        if version2.startswith("v"):
            version2 = version2[1:]

        # Split the versions into major, middle, and minor components
        major1, middle1, minor1 = version1.split(".")
        major2, middle2, minor2 = version2.split(".")

        # Compare the major components
        if major1 < major2:
            return True
        elif major1 > major2:
            return False

        # If major components are equal, compare the middle components
        if middle1 < middle2:
            return True
        elif middle1 > middle2:
            return False

        # If major and middle components are equal, compare the minor components
        if minor1 < minor2:
            return True
        elif minor1 > minor2:
            return False

        # The versions are equal
        return False

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
    except:
        return False

    setup_path = repository_path.replace(
        "https://github.com/", "https://raw.githubusercontent.com/"
    )
    online_version = await fetch_version_from_setup_file(
        f"{setup_path}/main/setup.py"
    )
    logging.info(
        f"version -> local: '{local_version}' | remote: '{online_version}'"
    )
    if is_older_version(online_version, local_version):
        return False
    return True


async def get_scraping_module(repository_path) -> ModuleType:
    module_name = os.path.basename(repository_path.rstrip("/"))
    if not await is_up_to_date(repository_path):
        subprocess.check_call(["pip", "install", f"git+{repository_path}.git"])
    loaded_module = import_module(module_name)
    return loaded_module
