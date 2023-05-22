import json, itertools, logging, aiohttp
from aiohttp import ClientSession


def create_session(*__args__, **__kwargs__):
    return ClientSession()


async def upload_to_ipfs(
    value, ipfs_path="http://ipfs-api.exorde.network/add"
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ipfs_path,
            data=json.dumps(value),
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status == 200:
                logging.debug("Upload to ipfs succeeded")
                response = await resp.json()
                return response
            else:
                content = await resp.text()
                logging.error(json.dumps(value))
                logging.error(json.dumps(content, indent=4))
                raise Exception(f"Failed to upload to IPFS ({resp.status})")


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


async def download_ipfs_file(hashname: str, max_attempts: int = 5):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
        "Connection": "close",
    }
    gateways = rotate_gateways()

    async with ClientSession(headers=headers) as session:
        for i in range(max_attempts):
            url = next(gateways) + hashname
            try:
                logging.info("download of %s (%s)", url, i)
                async with session.get(
                    url, timeout=20, allow_redirects=True
                ) as response:
                    if response.status == 200:
                        logging.info("download of %s OK after (%s)", url, i)
                        return await response.json()
            except:
                return None

    logging.error(
        f"Failed to download {hashname} after {max_attempts} attempts"
    )
