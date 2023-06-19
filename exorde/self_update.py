import os, subprocess
from importlib import metadata

from exorde.get_latest_tag import get_latest_tag


async def self_update():
    logging.info("[UDPATING] DISABLED FOR TESTING")
    return
    try:
        latest_tag = await get_latest_tag()
        local_version = metadata.version("exorde")
        if latest_tag != local_version:
            exorde_repository_path = "git+https://github.com/exorde-labs/exorde-client.git@auth_based_stateful#subdirectory=exorde&egg=exorde"
            subprocess.check_call(["pip", "install", exorde_repository_path])
            data_repository_path = "git+https://github.com/exorde-labs/exorde-client.git@auth_based_stateful#subdirectory=data&egg=exorde-data"
            subprocess.check_call(["pip", "install", data_repository_path])
            os._exit(42)
    except Exception as e:
        logging.info("[UDPATING] Error during self update: %s",e)
        
