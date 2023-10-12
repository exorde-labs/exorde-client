import os
import subprocess
from importlib import metadata
from packaging import version
import logging

from exorde.get_latest_tag import get_latest_tag


def normalize_version(version_string):
    """Normalize the version string and remove leading 'v' if it exists."""
    return (
        version_string[1:]
        if version_string.startswith("v")
        else version_string
    )


async def self_update():
    try:
        logging.info("[SELF CLIENT UPDATE] Checking...")
        # Try to get latest tag, if not possible, log and return
        try:
            latest_tag = await get_latest_tag()
        except Exception as e:
            logging.info(
                "[SELF CLIENT UPDATE] Unable to retrieve latest tag from GitHub: %s",
                e,
            )
            return

        # Try to get local version, if not found set default version
        try:
            local_version = metadata.version("exorde")
        except metadata.PackageNotFoundError:
            logging.info(
                "Package 'exorde' not found in the system. Setting default version"
            )
            local_version = "0.0.1"

        # Normalize the versions
        latest_tag = normalize_version(latest_tag)
        local_version = normalize_version(local_version)
        logging.info(
            f"[CLIENT VERSION] Online latest version of the exorde-client: {latest_tag}, local version: {local_version}"
        )

        try:
            if version.parse(latest_tag) > version.parse(local_version):
                logging.info(
                    f"[SELF CLIENT UPDATE] Updating from {local_version} to version {latest_tag}"
                )
                exorde_repository_path = (
                    "git+https://github.com/exorde-labs/exorde-client.git"
                )
                data_repository_path = (
                    "git+https://github.com/exorde-labs/exorde_data.git"
                )
                try:
                    subprocess.check_call(
                        ["pip", "install", "--user", exorde_repository_path]
                    )
                    subprocess.check_call(
                        ["pip", "install", "--user", data_repository_path]
                    )
                except subprocess.CalledProcessError as e:
                    logging.info(
                        "[SELF CLIENT UPDATE] Update failed, pip install returned non-zero exit status: %s",
                        e,
                    )
                    return
                os._exit(42)
        except version.InvalidVersion:
            logging.info("Error parsing version string")
    except Exception as e:
        logging.info("[SELF CLIENT UPDATE] Error during self update: %s", e)
