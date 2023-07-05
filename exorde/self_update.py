import os, subprocess
from importlib import metadata
from packaging import version

from exorde.get_latest_tag import get_latest_tag
import logging

def normalize_version(version_string):
    """Normalize the version string and remove leading 'v' if it exists."""
    return version_string[1:] if version_string.startswith('v') else version_string

async def self_update():
    try:
        latest_tag = await get_latest_tag()
        local_version = metadata.version("exorde")
        # Normalize the versions
        latest_tag = normalize_version(latest_tag)
        local_version = normalize_version(local_version)
        logging.info(f"[CLIENT VERSION] Online latest version of the exorde-client: {latest_tag}, local version:  {local_version}")        
        if version.parse(latest_tag) > version.parse(local_version):
            logging.info(f"[CLIENT UPDATE] Updating from {local_version} to version  {latest_tag}")
            exorde_repository_path = "git+https://github.com/exorde-labs/exorde-client.git@breeze"
            subprocess.check_call(["pip", "install", exorde_repository_path])
            data_repository_path = "git+https://github.com/exorde-labs/exorde-client.git@breeze#subdirectory=data&egg=exorde-data"
            subprocess.check_call(["pip", "install", data_repository_path])
            os._exit(42)
    except Exception as e:
        logging.info("[UPDATING] Error during self update: %s",e)
